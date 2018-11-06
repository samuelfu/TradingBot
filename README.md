# MIT_Trading

```
$ mangocore --help
Usage of mangocore:
  -case string
    	case file to load
  -identity string
    	identity file to load
  -logf string
    	log file format
  -mprofile
    	enable cpu profiling
  -port string
    	port to use (default ":10914")
  -profile
    	enable cpu profiling
  -speedup float
    	how many times faster mangocore should run (default 1)
  -start int
    	automatically start in given seconds
  -test
    	testing mode (default true)
```

Start the trading server using something like `./mangocore-osx-amd64.x -case /path/to/casefile`.

Start each bot as a standard python3 file.

## Barclays Options
Calculates the implied volatility of T100C whenever market updates

Uses the historical implied volatility to predict using polynomial regression future volatility (3 seconds out)

Calculate future price of T100C using future implied volatility

If future price > current price, purchase call option

If future price < current price, sell call option
