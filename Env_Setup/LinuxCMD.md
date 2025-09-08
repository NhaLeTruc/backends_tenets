# Useful Linux Commands

In essence, this command identifies all regular files larger than 100MB in the current directory and its subdirectories, then displays their details in a human-readable long listing format.

```bash
find . -size +100M -type f -exec ls -lh {} \;
```

The find command with the specified options is used to locate and display information about files larger than a certain size within a directory hierarchy.
Here's a breakdown of the command:

`find .`: This initiates the find command and specifies the starting point for the search as the current directory (.). The search will recursively descend into subdirectories.

`-size +100M`: This option filters the search results to include only files with a size greater than (+) 100 megabytes (M).

`-type f`: This option further refines the search to include only regular files (f), excluding directories, symbolic links, or other file types.

`-exec ls -lh {} \;`: This part of the command executes another command (ls -lh) for each file found by find.

`-exec`: This option tells find to execute the following command.

`ls -lh`: This is the command to be executed.

`ls`: Lists directory contents.

`-l`: Displays the output in a long listing format, providing detailed information like permissions, owner, group, size, and modification date.

`-h`: Displays file sizes in a human-readable format (e.g., 126M instead of bytes).

`{}`: This is a placeholder that find replaces with the name of each found file.

`\;`: This marks the end of the command being executed by -exec. It needs to be escaped (`\`) to prevent the shell from interpreting the semicolon as a command separator.
