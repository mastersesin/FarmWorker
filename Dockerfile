FROM python:3.9
WORKDIR /code

# Install application into container
COPY . .

RUN apt-get update && apt-get install git lsb-release sudo curl fuse -y

RUN pip install -r requirements.txt

RUN git clone https://github.com/Chia-Network/chia-blockchain.git -b latest --recurse-submodules

RUN cd chia-blockchain  && /bin/sh ./install.sh

RUN chia-blockchain/venv/bin/chia init -c ca

RUN python edit_plotting_and_config_file.py

RUN sudo -v ; curl https://rclone.org/install.sh | sudo bash

# Run the application
ENTRYPOINT ["/bin/sh","main.sh"]
