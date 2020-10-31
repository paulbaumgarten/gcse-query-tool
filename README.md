# gcse-query-tool

An sqlite tool to emulate the gcse query screen.

I'm a teacher of the iGCSE Computer Science course. The databases section of the course, while it does not explicitly require the use of Microsoft Access, infers it by requiring students to complete exam questions with a table that closely resembles the Access Query tool. An example of the GCSE question format follows...

![](gcse-question-example.png)

Personal;y, I dislike Access and don't want to teach or encourage my students to use it. I would much rather they learn an SQL based database, so I teach using SQLite. However, in order to properly prepare my students for their external exam, they do need some familiarity with this query screen.

To that end, I have created this Python project which will use an SQLite database to present a screen that sufficiently replicates the functionality of the Access Query tool for the purposes of the GCSE Computer Science course.

If you discover issues or have suggestions, please make contact with me. I'm happy to accept contributions from others that improve the project as well.

---

## Installation

The project is just one file and only imports from the standard library. The only task for installation is to download the file.

To run the project, just open the file and run it from your favourite Python editor.

If you wish to use the Windows command line...

```dos
python query-tool.py
```

Or for the Mac or Linux command line...

```bash
python3 query-tool.py
```

A sample database `demo.db` has also been provided.

If you need to create (or modify) an SQLite database for use with this tool, I suggest DB Browser from https://sqlitebrowser.org/

## Known issues / to-do list:

 * Needs vertical & horizontal scrolling for when dataset requires it.
 * Allow for SQL queries that join multiple tables.

## Author

Paul Baumgarten - [https://pbaumgarten.com/](https://pbaumgarten.com/)
