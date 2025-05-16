# CatFS - A Cat File System for CS 377 Group Project


## Authors

- Kimleng Kit
- David Zhan
- Rihui Lu

## Running the Project

Make sure you have Python 3 installed. This code is tested extensively on Python 3.12.1, so I would recommend using that version. There are no dependencies to install, so you can run the code directly.

All commands below assume that you have Python 3 installed as `python3`. If you have Python 3 installed as `python`, you can replace `python3` with `python` in all commands below.

### Running the Main Program

**To open or create** a cafe with name `cafe_name` run:

```bash
python3 main.py [cafe_name]
```

If you reopen a cafe with the same name, it will load you into the state that you left off at.

There are two optional flags you can use:
- `-c [cache_size]`: specifies enabling the cache with size cache_size
- `-p [visitor or volunteer or staff or admin]` sets the role that you want to open the file system with

In order to get a summary of what flags are available, run:

```bash
python3 main.py -h
```

### Running the Tests

To run the **unit tests** for the project, run:

```bash
python3 tests/unit.py
```

To run the **performance tests** for the project, run:

```bash
python3 tests/performance.py
```

> *this may take a while to run*

