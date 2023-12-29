FROM condaforge/miniforge3:23.3.1-1

EXPOSE 5006
CMD conda run --no-capture-output -n visualiser-env python -O main.py

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY environment.yml requirements.txt ./
RUN conda env create -f environment.yml
COPY . .

