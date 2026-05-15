How to run simulations

use ~/opp_repl to run simulations.
it has extensive documentation as well.

alternatively:

- run `. setenv` in ~/omnetpp-dev
- run `. setenv` in ~/inet
- in the folder of the simulation, run simulation with `inet_dbg -u Cmdenv -c <config_name> --cmdenv-express-mode=false --cmdenv-log-level=<log_level> --mcp-server-address localhost:<8765>`
- you only have to run the setenv commands once per terminal session