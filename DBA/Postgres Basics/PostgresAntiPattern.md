# SQL Antipatterns

## Logical Database Design Antipatterns

Before you start coding, you should decide what information you need to keep in your database and the best way to organize and interconnect your data. This includes planning your database tables, columns, and relationships.

## Physical Database Design Antipatterns

After you know what data you need to store, you implement the data management as efficiently as you can using the features of your RDBMS technology. This includes defining tables and indexes and choosing data types. You use SQL’s data definition language—statements such as CREATE TABLE.

## Query Antipatterns

You need to add data to your database and then retrieve data. SQL queries are made with data manipulation language—statements such as SELECT, UPDATE, and DELETE.

## Application Development Antipatterns

SQL is supposed to be used in the context of applications written in another language, such as C++, Java, PHP, Python, or Ruby. There are right ways and wrong ways to employ SQL in an application, and this part of the book describes some common blunders.

## Anatomy of an Antipattern

Each antipattern chapter contains the following subheadings:

### Objective

This is the task that you may be trying to solve. Antipatterns are used with an intention to provide that solution but end up causing more problems than they solve.

### The Antipattern

This section describes the nature of the common solution and illustrates the unforeseen consequences that make it an antipattern.

### How to Recognize the Antipattern

There may be certain clues that help you identify when an antipattern is being used in your project. Certain types of barriers you encounter, or quotes you may hear yourself or others saying, can
tip you off to the presence of an antipattern.

### Legitimate Uses of the Antipattern

Rules usually have exceptions. There may be circumstances in which an approach normally considered an antipattern is nevertheless appropriate, or at least the lesser of all evils.

### Solution

This section describes the preferred solutions, which solve the original objective without running into the problems caused by the antipattern.
