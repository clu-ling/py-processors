# FAQ

### I want the latest `processors-server.jar`
In that case, take a look over [here](https:github.com/myedibleenso/processors-server).

### Something is already running on port `XXXX`, but I don't know what.  Help!

Try running the following command:

```bash
lsof -i :<portnumber>
```
You can then kill the responsible process using the reported `PID`

### Does `py-processors` produce a (server) log?

Yep!  By default, it will write to `~/py-processors.log`.  You can specify a different location when initializing the API:

```python
from processors import *

API = ProcessorsAPI(port=8886, log_file="my/desired/log/file.log")
```
