<center>
    <h1> Window Recall for Linux</h1>
    <h6>To be renamed soon<br/>
     Currently in proof of concept stage</h6>
</center>

## Introduction
This is a simple program that is kind of like the new Windows recall feature. 

## Disclaimer/Notes
- I am not a AI expert or a machine learning expert. I am just a student who is trying to build some stuff by FAFO.
- This is a proof of concept and is not meant to be used in production.
- This hasn't been tested on any other system other than my own. So, it might not work on your system.
    - This will work on KDE Wayland provided you install the necessary dependencies.
    - Currently its Linux only but may soon add support for Windows and MacOS.
- This will probably drain your battery. So, use it at your own risk.
- This program doesn't provide any sort of encryption or security(yet). So, use it at your own risk.

## Dependencies/Pre-requisites
###### Since it's just a proof of concept, I haven't added any checks for the dependencies. So, you need to install them manually.

- Have [ollama](ollama.com/) installed and running with the following models downloaded
    - phi3
    - moondream
    - mxbai-embed-large
- [Docker](https://docs.docker.com/engine/install/) (Will be used for Qdrant database)
- Have [Qdrant](https://qdrant.tech/documentation/quick-start/) installed and running 
- [kdotool](https://github.com/jinliu/kdotool) (Might already be in your package manager)
- [tesseract](https://github.com/tesseract-ocr/tesseract)


## How to run?
- Make sure ollama & Qdrant are running.
- Install requirements using `pip install -r requirements.txt`
- Run the `service.py` file in the background so that it automatically takes screenshots. (Preferrably set it up as a service on ur system or have it on auto start)

- Run `client.py` to use the GUI. (Currently its very barebone, I will improve it overtime)


## To Do 
- Add support for other Linux environments
- Add support for Windows and MacOS
- Add more features to the client
- Improve the prompts
- Save the files opened by a program as well.
- Add option to reopen the files in the same program
- Add option to reopen the files in a different program
- Experiment with different models and see which one works best
- Improve the UI of the client
- Add encryption and security


Liked my efforts? Consider sponsoring me on GitHub or buying me a coffee.

[![GitHub Sponsor](https://img.shields.io/badge/Sponsor-GitHub-%23EA4AAA?logo=GitHub)](https://github.com/sponsors/notnotrachit)

Also, please star the repo, it motivates me to work on it more.
![GitHub Repo stars](https://img.shields.io/github/stars/notnotrachit/recall?style=social)
