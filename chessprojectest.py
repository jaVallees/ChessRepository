import requests
import pandas as pd
import chess.pgn
import io
from datetime import datetime, timedelta

USERNAME = "javalle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_json(url):
    """Fetch JSON data from an API with error handling."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from {url} (Status Code: {response.status_code})")
        return None
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {url}")
        return None

# Get player ID
player_url = f"https://api.chess.com/pub/player/{USERNAME}"
player_data = fetch_json(player_url)

if player_data:
    player_id = player_data.get("player_id", "Unknown")
else:
    print("Failed to fetch player information.")
    player_id = "Unknown"

# Get the last full week range (Monday to today)
today = datetime.today()
start_of_week = today - timedelta(days=today.weekday() + 7)  # Last Monday
end_of_week = today  # Ensure we get up to today

# Fetch games for the affected month(s), including the current one
months_needed = {
    start_of_week.strftime("%Y/%m"),
    end_of_week.strftime("%Y/%m"),
    today.strftime("%Y/%m")  # Ensures today's games are included
}

all_games = []
for year_month in months_needed:
    pgn_url = f"https://api.chess.com/pub/player/{USERNAME}/games/{year_month}/pgn"
    response = requests.get(pgn_url, headers=HEADERS)

    if response.status_code == 200 and response.text.strip():
        all_games.extend(response.text.strip().split("\n\n\n"))
    else:
        print(f"Error: Unable to fetch PGN data from {pgn_url} (Status Code: {response.status_code})")

# Process Games
match_records = []
for game_pgn in all_games:
    game_io = io.StringIO(game_pgn)
    game = chess.pgn.read_game(game_io)

    if game:
        game_date_str = game.headers.get("Date", "Unknown")
        try:
            game_date = datetime.strptime(game_date_str, "%Y.%m.%d")
        except ValueError:
            continue  # Skip invalid dates

        # Ensure all games up to today are included
        if start_of_week <= game_date <= end_of_week:
            moves_list = [str(move) for move in game.mainline_moves()]
            move_count = len(moves_list)
            avg_move_length = sum(len(move) for move in moves_list) / move_count if move_count else 0

            match_records.append({
                "Date": game_date,
                "Player_ID": player_id,
                "White_Player": game.headers.get("White", "Unknown"),
                "Black_Player": game.headers.get("Black", "Unknown"),
                "Result": game.headers.get("Result", "Unknown"),
                "Opening": game.headers.get("ECOUrl", "Unknown").split("/")[-1] if game.headers.get("ECOUrl") else "Unknown",
                "Time_Control": game.headers.get("TimeControl", "Unknown"),
                "Termination": game.headers.get("Termination", "Unknown"),
                "Move_Count": move_count,
                "Avg_Move_Length": round(avg_move_length, 2),
                "Moves": " ".join(moves_list)
            })

# Convert to DataFrame and sort by date
df = pd.DataFrame(match_records).sort_values(by="Date", ascending=True)

# Calculate Performance for Last Week
if not df.empty:
    total_games = len(df)
    wins = df[df["Result"] == "1-0"].shape[0]
    losses = df[df["Result"] == "0-1"].shape[0]
    draws = df[df["Result"] == "1/2-1/2"].shape[0]
    win_percentage = (wins / total_games) * 100 if total_games > 0 else 0

    print("\nGames Played Last Week:")
    print(df[["Date", "White_Player", "Black_Player", "Result", "Opening", "Move_Count"]])

    print(f"\nPlayer {USERNAME} Performance ({start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}):")
    print(f"Total Games: {total_games}")
    print(f"Wins: {wins}, Losses: {losses}, Draws: {draws}")
    print(f"Win Percentage: {win_percentage:.2f}%")
else:
    print("\nNo games found for last week.")
