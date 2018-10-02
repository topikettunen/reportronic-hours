# Reportronic Hours

## Local Install

- Clone this repository

```
$ git clone git@github.com:topikettunen/reportronic-hours.git
```

- Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and insert it in PATH in Linux/macOS or root of this repo on Windows.

- Install dependencies (with `pipenv`):

```
$ cd reportronic-hours
$ pipenv install
```

- Install dependencies (with `pip`):

```
$ cd reportronic-hours
$ pip install -r requirements.txt
```

## Run Script

Scripts for running this script can be found from `utils` dir.
In case you want to run scripts via `pipenv` remember to add `pipenv run`
before the `python` command that is found in the script.

Scripts found are:

  - `run-script.sh` for regular run that uses `python3` for running script.
  - `run-script-win.sh` for running script on Windows. Uses Python3 but by default uses `python` as binary.
  - `xvfb-run-script.sh` for running script on headless state.
  
Run script via:

```
$ ./run-script.sh --help
```

Possible options currently are:

  - `--monthly` for monthly script run.
  - `--daily` for daily script run.
  - `--friday` for specialized script run for Fridays.
  - `--delete-duplicate` for deleteing possible earlier entries for today.

## Run Script in Docker container

- Clone repo:

```
$ git clone git@github.com:topikettunen/reportronic-hours.git
```

- Build the image:

```
$ cd reportronic-hours
$ docker build -t reportronic-hours .
```

- Run the script inside Docker container:

```
$ docker run --rm reportronic-hours --daily
```
