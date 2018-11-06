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
### Case Information:

The trade-able instruments are options and TMXFUT futures, where the futures are solely for hedging. Both are cash-settled.

There are 82 options in each round of the case: 41 puts and 41 calls, in range(80, 121).

Options expire at the end of each round and their tickers are subsequently re-used.

Five example tickers are listed below; other tickers follow the same naming conventions:

| Strike Price  | Put Option Ticker | Call Option Ticker |
| ------------- | -------------     |-------------       |
| $90           |              T90P |    T90C            |
| $95           |              T95P |    T95C            |
| $100          |              T100P|    T100C           |
| $105          |              T105P|    T105C           |

The ticker for futures on the index is “TMXFUT”

### File information
'example_bot.py'

Calculates the implied volatility of T100C whenever market updates

Uses the historical implied volatility to predict using polynomial regression future volatility (3 seconds out)

Calculate future price of T100C using future implied volatility

If future price > current price, purchase call option

If future price < current price, sell call option
