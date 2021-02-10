FROM continuumio/miniconda3:4.9.2

EXPOSE 5006
CMD conda run --no-capture-output -n visualiser-env python main.py

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY environment.yml requirements.txt ./
RUN conda env create -f environment.yml
COPY . .

