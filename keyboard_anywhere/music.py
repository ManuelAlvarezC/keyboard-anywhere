import time

import fluidsynth
import numpy as np
from OpenGL import GL as ogl


PLAY_TIME = 0.1            # Minimum time a note will sound for
REPEAT_TIME = 0.1          # Minimum time between the start of two notes
SAMPLE_STRIDE = 2          # Divide depth map resolution by this amount
MIN_POINTS = 4             # Minimum points in a key for it to be pressed

KB_WIDTH_FAC = 0.1         # Width of keyboard = Length * KB_WIDTH_FAC
KB_HEIGHT_FAC = 0.01       # Height of keyboard = Length * KB_HEIGHT_FAC
KB_GAP_FAC = 0.01          # Gap between keys = KB Length * KB_GAP_FAC

KB_NUM_KEYS = 22           # Only dealing with white keys for now
KB_START_KEY = 0           # 0 = C2, 1 = D2, etc... (whites only)


class Key(object):
    """ Represents a key's state, position and colour. """

    def __init__(self, note, vmin, vmax, colour=(1, 1, 1, 0.5)):
        """Create a key corresponding to a midi note."""
        self.note = note
        self.vmin = np.array(vmin)
        self.vmax = np.array(vmax)
        self.colour = colour
        self.quads = self.get_quads(self.vmin, self.vmax)
        self.pressed = False
        self.last_pressed = 0

        self.synth = fluidsynth.Synth()
        self.synth.start('alsa')
        sfid = self.synth.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
        self.synth.program_select(0, sfid, 0, 0)

    @staticmethod
    def get_quads(vmin, vmax):
        """ Return the 6 faces of a rectangluar prism defined by (vmin, vmax). """
        x1, y1, z1, x2, y2, z2 = np.hstack((vmin, vmax))

        return np.array([
            [x1, y1, z1], [x1, y2, z1], [x2, y2, z1], [x2, y1, z1],
            [x1, y1, z2], [x2, y1, z2], [x2, y2, z2], [x1, y2, z2],
            [x1, y1, z1], [x1, y1, z2], [x1, y2, z2], [x1, y2, z1],
            [x2, y1, z1], [x2, y2, z1], [x2, y2, z2], [x2, y1, z2],
            [x1, y1, z1], [x2, y1, z1], [x2, y1, z2], [x1, y1, z2],
            [x1, y2, z1], [x1, y2, z2], [x2, y2, z2], [x2, y2, z1]]).T

    def update(self, points):
        """ Update the key's press status by using the 3D points. """
        # Compute how many points are within the extents of the key
        big_enough = (points > self.vmin.reshape((3, -1))).min(axis=0)
        small_enough = (points < self.vmax.reshape((3, -1))).min(axis=0)
        inkey_indices = np.multiply(big_enough, small_enough)

        if(sum(inkey_indices) > MIN_POINTS):
            self.press()
        else:
            self.release()

    def press(self):
        """ Plays the note if the key was previously unpressed. """
        press_time = time.clock()

        if not(self.pressed) and press_time - self.last_pressed > PLAY_TIME:
            self.pressed = True
            self.synth.noteon(0, self.note, 127)
            self.last_pressed = press_time

    def release(self):
        """ Stop the note if the key was previously pressed. """
        unpress_time = time.clock()

        if self.pressed and unpress_time - self.last_pressed > REPEAT_TIME:
            self.pressed = False
            self.synth.noteoff(0, self.note)


class Keyboard(object):
    """ Represents the virtual keyboard.

    Handles drawing as well as math for transformations.

    """

    def __init__(self):
        """ Create the keyboard. """

        self.vmin = np.array([0, 0, 0])
        self.vmax = np.array([1, KB_WIDTH_FAC, KB_HEIGHT_FAC])

        # Load previous transform from file (if exists)
        try:
            self.set_transform(np.load('keyboard_transform.npy'))
            print('transform loaded from file')
        except FileNotFoundError:
            print('failed to load from file')
            self.set_transform(np.diag([100, 100, 100, 1]))

        # Compute the midi note value for a few octaves
        white_basis = np.array([0, 2, 4, 5, 7, 9, 11])
        white_notes = np.hstack((
            white_basis + 36,
            white_basis + 48,
            white_basis + 60,
            white_basis + 72
        ))

        def make_white_key(number, note):
            xmin = number * 1.0 / KB_NUM_KEYS + KB_GAP_FAC / 2
            xmax = (number + 1) * 1.0 / KB_NUM_KEYS - KB_GAP_FAC / 2
            ymin = self.vmin[1]
            ymax = self.vmax[1]
            zmin = self.vmin[2]
            zmax = self.vmax[2]
            return Key(note, [xmin, ymin, zmin], [xmax, ymax, zmax])

        whites = white_notes[KB_START_KEY:KB_START_KEY + KB_NUM_KEYS]
        self.keys = list(map(make_white_key, range(0, KB_NUM_KEYS), whites))

        # Create the synthesiser - and pass it to Key class
        self.synth = fluidsynth.Synth()
        self.synth.start('alsa')
        sfid = self.synth.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
        self.synth.program_select(0, sfid, 0, 0)
        Key.synth = self.synth

    def set_transform(self, transform):
        """ Update the internal transform, calculate inverse, and save it. """
        self.transform = transform
        self.inv_transform = np.linalg.inv(transform)
        np.save('keyboard_transform', self.transform)

    def nudge_roll(self, sign):
        """ Rotate about local y axis. """
        delta = np.eye(4)
        t = sign * 0.001
        c, s = np.cos(t), np.sin(t)

        Ry = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
        delta[0:3, 0:3] = Ry

        new_t = np.dot(self.transform, delta)
        self.set_transform(new_t)

    def nudge_z(self, sign):
        """ Move along local z axis. """
        delta = np.zeros((4, 4))
        translation = self.transform[0:3, 2] * 0.001 * sign
        delta[0:3, 3] = translation
        self.set_transform(self.transform + delta)

    def update(self, points):
        """ Update state using points """

        # Convert points into local coordinate frame
        H = self.inv_transform
        pointsT = np.dot(H[0:3, 0:3], points) + H[0:3, 3].reshape((3, 1))

        # Clip to keyboard dimensions (speeds up later processing)
        big_enough = (pointsT > self.vmin.reshape((3, -1))).min(axis=0)
        small_enough = (pointsT < self.vmax.reshape((3, -1))).min(axis=0)
        valid_indices = np.multiply(big_enough, small_enough)
        valid_pts = pointsT[:, valid_indices]

        # Update all the keys
        for k in self.keys:
            k.update(valid_pts)

    def draw(self):
        """ Draw the keys. """

        ogl.glPushMatrix()
        ogl.glMultMatrixf(self.transform.T)

        # Draw notes
        for k in self.keys:
            if k.pressed:
                ogl.glColor4fv([0, 1, 0, 0.4])
            else:
                ogl.glColor4fv(k.colour)
            ogl.glVertexPointer(3, ogl.GL_FLOAT, 0, k.quads.T)
            ogl.glDrawArrays(ogl.GL_QUADS, 0, k.quads.shape[1])

        ogl.glPopMatrix()
