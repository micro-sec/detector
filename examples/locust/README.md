## Run Locust

```bash
cd examples/locust
python3 -m locust -f locust_sockshop_browse_variable.py --host http://10.3.1.45 -t 1800s --csv=logs/logs
```