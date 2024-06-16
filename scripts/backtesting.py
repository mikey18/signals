import pandas as pd
import numpy as np
import vectorbt as vbt

def calculate_phases(initial_balance, risk, stop_loss_pips, pip_value):
    money_to_risk = initial_balance * risk
    initial_lot_size = 0.04
    phases = {
        1: [(initial_lot_size, 250, 750), (initial_lot_size, 250, 750), (initial_lot_size, 500, 1500), (initial_lot_size, 1000, 3000)],
        2: [(2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 500, 1500), (2 * initial_lot_size, 1000, 3000)],
        3: [(3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 500, 1500), (3 * initial_lot_size, 1000, 3000)],
        4: [(4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 500, 1500), (4 * initial_lot_size, 1000, 3000)]
    }
    return phases

# Load and preprocess data
data_path = 'new.csv'  # Replace with the actual file name
df = pd.read_csv(data_path)
df.columns = ['date_time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
df['date_time'] = pd.to_datetime(df['date_time'], format='%Y-%m-%d %H:%M:%S')
df.sort_index(inplace=True)
df.dropna(axis=1, how='all', inplace=True)
df.fillna(method='ffill', inplace=True)

# Calculate indicators
sma_14 = vbt.MA.run(df['close'].values, window=14)
sma_50 = vbt.MA.run(df['close'].values, window=50)
sma_365 = vbt.MA.run(df['close'].values, window=365)
rsi = vbt.RSI.run(df['close'].values, window=14)

# Define strategy logic for both buy and sell
buy_signal = (sma_14.ma > sma_50.ma) & (sma_50.ma > sma_365.ma) & (rsi.rsi < 40)
sell_signal = (sma_14.ma < sma_50.ma) & (sma_50.ma < sma_365.ma) & (rsi.rsi > 60)

# Count the number of signals
num_buy_signals = buy_signal.sum()
num_sell_signals = sell_signal.sum()

print(f"Number of Buy Signals: {num_buy_signals}")
print(f"Number of Sell Signals: {num_sell_signals}")

# Initialize parameters
initial_cash = 100000
initial_balance = initial_cash
risk = 0.01
stop_loss_pips = 250
pip_value = 0.01

# Calculate phases
phases = calculate_phases(initial_cash, risk, stop_loss_pips, pip_value)

# Initialize vectors for the strategy
current_phase = 1
current_step = 0
current_balance = initial_cash
in_trade = False
trade_type = None
total_trades = 0
wins = 0
losses = 0
consecutive_wins = 0
consecutive_losses = 0
max_consecutive_wins = 0
max_consecutive_losses = 0
last_trade_result = None

# Create an empty DataFrame to store trade results
trade_results = pd.DataFrame(columns=['Date', 'Trade Type', 'Trade Result', 'Balance', 'Entry Price', 'Lot Size', 'Stop Price', 'Take Profit Price', 'Current Phase', 'Current Step', 'Next Phase', 'Next Step'])

# Implement the strategy
start_index = max(365, 14)  # Ensure at least the largest lookback period

for i in range(start_index, len(df)):
    if not in_trade:
        if buy_signal[i]:
            trade_type = 'BUY'
            in_trade = True
        elif sell_signal[i]:
            trade_type = 'SELL'
            in_trade = True
        
        if in_trade:
            total_trades += 1
            lot_size = phases[current_phase][current_step][0]
            stop_loss_pips = phases[current_phase][current_step][1]
            take_profit_pips = phases[current_phase][current_step][2]

            entry_price = df['close'][i]
            if trade_type == 'BUY':
                stop_price = entry_price - (stop_loss_pips * pip_value)
                take_profit_price = entry_price + (take_profit_pips * pip_value)
            else:  # SELL
                stop_price = entry_price + (stop_loss_pips * pip_value)
                take_profit_price = entry_price - (take_profit_pips * pip_value)

    elif in_trade:
        close_price = df['close'][i]
        
        if trade_type == 'BUY':
            if close_price >= take_profit_price or close_price <= stop_price:
                in_trade = False
        else:  # SELL
            if close_price <= take_profit_price or close_price >= stop_price:
                in_trade = False

        if not in_trade:  # Trade closed
            if (trade_type == 'BUY' and close_price >= take_profit_price) or (trade_type == 'SELL' and close_price <= take_profit_price):
                pnl = take_profit_pips * pip_value * lot_size * 100
                current_balance += pnl
                wins += 1
                consecutive_wins += 1
                consecutive_losses = 0
                if consecutive_wins > max_consecutive_wins:
                    max_consecutive_wins = consecutive_wins
                last_trade_result = 'win'
                trade_result = 'PROFIT'

                if current_balance > initial_balance:
                    initial_balance = current_balance
                    next_phase = 1
                    next_step = 0
                else:
                    next_phase = current_phase
                    next_step = 0

            else:  # Stop loss hit
                pnl = -stop_loss_pips * pip_value * lot_size * 100
                current_balance += pnl
                losses += 1
                consecutive_losses += 1
                consecutive_wins = 0
                if consecutive_losses > max_consecutive_losses:
                    max_consecutive_losses = consecutive_losses
                last_trade_result = 'loss'
                trade_result = 'LOSS'

                next_step = current_step + 1
                if next_step >= len(phases[current_phase]):
                    next_step = 0
                    next_phase = current_phase + 1
                    if next_phase > len(phases):
                        next_phase = 1
                else:
                    next_phase = current_phase

            # Record trade results
            trade_results = pd.concat([trade_results, pd.DataFrame([{
                'Date': df.iloc[i]['date_time'],
                'Trade Type': trade_type,
                'Trade Result': trade_result,
                'Balance': current_balance,
                'Entry Price': entry_price,
                'Lot Size': lot_size,
                'Stop Price': stop_price,
                'Take Profit Price': take_profit_price,
                'Current Phase': current_phase,
                'Current Step': current_step + 1,
                'Next Phase': next_phase,
                'Next Step': next_step + 1
            }])], ignore_index=True)
            print(f"{df.iloc[i]['date_time']} - {trade_type} Trade Result: {trade_result}, Balance: {current_balance:.2f}")
            print(f"Entry Price: {entry_price}, Lot Size: {lot_size:.2f}, Stop Price: {stop_price:.2f}, Take Profit Price: {take_profit_price:.2f}")
            print(f"Current Phase: {current_phase}, Current Step: {current_step + 1}")
            print(f"Next Phase: {next_phase}, Next Step: {next_step + 1}")

            # Update current phase and step for the next iteration
            current_phase = next_phase
            current_step = next_step

# Print final balance
print(f"Final Balance: {current_balance:.2f}")

# Print strategy summary
print('--- Strategy Summary ---')
print(f'Total Trades: {total_trades}')
print(f'Wins: {wins}')
print(f'Losses: {losses}')
print(f'Win Percentage: {wins / total_trades * 100:.2f}%')
print(f'Loss Percentage: {losses / total_trades * 100:.2f}%')
print(f'Max Consecutive Wins: {max_consecutive_wins}')
print(f'Max Consecutive Losses: {max_consecutive_losses}')
print(f'Last Trade Result: {last_trade_result}')
print('-------------------------')

# Create summary dictionary
summary = {
    'Metric': ['Final Balance', 'Total Trades', 'Wins', 'Losses', 'Win Percentage', 'Loss Percentage', 'Max Consecutive Wins', 'Max Consecutive Losses', 'Last Trade Result'],
    'Value': [f"{current_balance:.2f}", total_trades, wins, losses, f"{wins / total_trades * 100:.2f}%", f"{losses / total_trades * 100:.2f}%", max_consecutive_wins, max_consecutive_losses, last_trade_result]
}

# Convert summary to DataFrame
summary_df = pd.DataFrame(summary)

# Append summary to trade results
trade_results = pd.concat([trade_results, summary_df], ignore_index=True)

# Export trade results to CSV
trade_results.to_csv('trade_results.csv', index=False)