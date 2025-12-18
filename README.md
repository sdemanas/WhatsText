# WhatsText
WhatsText makes WhatsApp chat exports more readable and interesting.

- [Why?](#Why?)
- [Installation](#Installation)
    - Method 1: pypi
    - Method 2: Install From Source
- [Dependencies](#Dependencies)
- [Usage](#Usage)
- [Configuration](#Configuration)
- [Output Structure](#Output)
- [ChangeLog](/Changelog.md)
- [Want to Contribute?](#Contribute)
- [References](#FOSS)

## Why ?
Whatsapp export chats exports it to a text file with a media attachments in a folder **which is boring.**

### Features 

**0.1.0**

- [x] Parsing Chat Log for regular chats 
- [x] Parsing Attachments

0.1.2

- [ ] Parsing for Group Chats

1.0

- [ ] 3 Themes to choose from 
- [ ] Light/Dark Mode

**WhatsText makes that interesting.**

### Demo 




All you need to do is to install the python package and run it against your chat export.

## Installation

1. Use Pip to install WhatsText on your machine 
```pip install WhatsText```

2. Download the project onto your local machine and run 
```python main.py 'path/to/file/_chat.txt'```

## Dependencies

- Standard python libraries 

## Usage

```python main.py 'path/to/file/_chat.txt'```

## Configuration

- Yet to add customizability

## Output 

- Output generated as a zip in  ```path/to/file```

## Contribute
This project is open for contribution, as long as it remains useful.

### Raise an Issue
- If you find and issue please report it by creating a new issue at 
https://github.com/sdemanas/WhatsText/issues

- If a similar issue already exists please add to the same.

### Create a PR

To submit a new feature request raise an issue, describe your requirements and create a PR.


### Active Maintainers

[sdemanas](https://github.com/sdemanas)

## FOSS

List of open source projects and references used for building WhatsText 

https://jinja.palletsprojects.com/en/stable/

https://github.com/Textualize/rich