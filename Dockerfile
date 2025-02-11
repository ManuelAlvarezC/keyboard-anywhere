FROM python:3.4

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1
ENV APT_LISTCHANGES_FRONTEND=none

# Completely rewrite sources.list to avoid missing repos
RUN echo "deb http://archive.debian.org/debian stretch main" > /etc/apt/sources.list

# Ensure APT does not attempt to use missing repositories
RUN apt-get clean && apt-get update -o Acquire::Check-Valid-Until=false


# Basic systen update and pruning
RUN apt update && apt -y upgrade && apt -y autoremove

# Install system dependencies for sound, image and the rest of the fray
RUN apt -y install cmake build-essential libusb-1.0-0-dev freeglut3-dev libxmu-dev libxi-dev fluidsynth fluid-soundfont-gm git-core python3 python3-dev software-properties-common python3-launchpadlib libqt4-dev pyqt4-dev-tools qt4-dev-tools qt4-qmake python-qt4 libqt4-declarative libqt4* libqtcore4 libqtgui4 libqtwebkit4 qt4*

# Set working directory
COPY . /app/
WORKDIR /app

# Install freenect drivers
RUN chmod a+x /app/scripts/install_freenect.sh
RUN /app/scripts/install_freenect.sh

RUN apt update && apt install -y python-qt4
RUN pip install --upgrade pip && pip install .

ENTRYPOINT ["python", "display_kinnect.py"]