# HeaderGraphPartioning
Scripts used to generate a graph suggesting possible partitions for a header.

Run the following scripts on the first run. If you want to test for different compile_commands.json you will need to rerun this:

```bash
python process_ast.py -c compile_commands.json > ast_dump.txt
python ast_json.py -f ./ast_dump.txt
```

Replace compile_commands.json with the relative or absolute location. 
Optionally add -c and a filename to the ast_json invocation if you want to specify a file other than the auto generated outfile.json.


```bash
python hierarchical_agglomeration.py -f ../linux/include/linux/string.h -c outfile.json
```

Replace with the appropriate header file location.
Optionally add -d to find proximity betwen different tokens for further analysis.
