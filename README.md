# HeaderGraphPartioning
Scripts used to generate a graph suggesting possible partitions for a header.

Run the following scripts on the first run. If you want to test for different compile_commands.json you will need to rerun this:

```bash
python ast_json.py -c compile_commands.json
```

Replace compile_commands.json with the relative or absolute location. 
Optionally add -c and a filename to the ast_json invocation if you want to specify a file other than the auto generated outfile.json.

This command generates a json file that is consumed by hierarchical_agglomeration.py.
Invoke it using the following command to generate a graph that suggest a partition in headers.


```bash
python hierarchical_agglomeration.py -f ../linux/include/linux/string.h -c outfile.json
```

Replace with the appropriate header file location.
Optionally add -d to find proximity betwen different tokens for further analysis.

Below is an example graph of linux/types.h:
![Alt](/images/Figure_1.png)
