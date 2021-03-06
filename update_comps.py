import import_data
import pandas as pd
import matplotlib.pyplot as plt

config = import_data.get_config("test/config.json")
# comps = import_data.get_comps(config)
# comp_funds = import_data.get_comp_fundamentals([*comps["ticker"]])

comps = pd.read_csv("test/comps.csv")
comp_funds = import_data._read_and_standardize("test/comp_funds.csv", col=["calendardate", "ticker"])


# BASIC COMPS
comp_funds_latest = comp_funds.groupby("ticker").apply(lambda x: x[x.index.get_level_values(0) == max(x.index.get_level_values(0))])
# leave only latest metrics
comp_funds_latest.index = comp_funds_latest.index.droplevel(0)
# keep ticker as index

comps_merged = pd.merge(left=comp_funds_latest, right=comps, 
                        on=["ticker"], left_index=True,
                        how="left")

comps_merged = comps_merged[["name", "ticker", "price", "marketcap", "ev/ebitda", "ev/sales", "ev/fcf"]]
# maintail relevant columns
comps_merged = import_data.round_col(comps_merged, ["marketcap"], to="B")
comps_merged.loc[:, "price":] = comps_merged.loc[:, "price":].apply(lambda x: round(x, 2))

comps_merged.columns = ["Name", "Ticker", "Stock Price", "Market Cap.", "EV/EBITDA", "EV/SALES", "EV/FCF"]
comps_merged = comps_merged.set_index("Ticker")
# make ticker index

comps_merged.to_csv("charts/comps.csv")

## COMPS GRAPH
# TODO remobe the comments
# etf = import_data.get_etf(config)
# sp500 = import_data.get_sp500()

tickers = list(comps.ticker.unique())

# daily = import_data.get_daily_metrics(tickers, config)
daily = import_data._read_and_standardize("test/daily.csv", col=["date", "ticker"])

daily_prices = daily.close
daily_evebitda = daily.evebitda
del daily

#daily_prices = pd.concat(daily_prices, etf, sp500)
#del etf
#del sp500

fun = lambda x: (x / x.loc[(x.index.get_level_values(0).min(), x.index.get_level_values(1)[0])]) * 100
# indexing function
daily_prices = daily_prices.groupby("ticker").transform(fun)

def plot_groups(ts, level=1, drop_level=None, ax=None, colors=["red", "green", "blue", "orange", "yellow", "purple"]):
    """Plot a time-series by a grouped level

    Precondition: len(groups) <= 6
    groups to be plotted based on index
    """

    grouped = ts.groupby(level=level)

    for i, group_info in enumerate(grouped):

        if drop_level:
            group_info[1].index = group_info[1].index.droplevel(drop_level)

        group_info[1].plot(ax=ax, color=colors[i])
        # plot grapth for each group precondition of at most 6 groups

fig = plt.figure()

ax1 = fig.add_subplot(211)

plot_groups(daily_prices, level=1, drop_level=1, ax=ax1)

ax1.set_xlabel(None)
ax1.set_ylabel("Indexed Stock Price")
ax1.legend("upper right")

plt.grid()

ax2 = fig.add_subplot(212, sharex=ax1)

plot_groups(daily_evebitda, level=1, drop_level=1, ax=ax2)

ax2.set_xlabel(None)
ax2.set_ylabel("EV/EBITDA")
ax2.legend("upper right")

plt.grid()

fig.savefig("charts/comps_graph.jpg")
