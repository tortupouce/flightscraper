````markdown
# ✈️ Flightscraper

This is a Python command-line tool for searching cheap flights using the Amadeus API with support for:
- Flexible travel dates (single or range)
- Custom passenger combinations (adults, seniors, students, children, infants)
- Optional stopover city logic (e.g. simulate layovers to find cheaper routes)
- Booking link generation via Kayak.com

---

## 🚀 Features

- ✅ Search flights by origin/destination and date or date range
- ✅ Filter by custom passenger types and counts
- ✅ Simulate multi-leg trips via manual stopovers (like "hacking" cheaper flights)
- ✅ Automatically generates clickable Kayak booking links matching your search
- ✅ Built-in debug output to help troubleshoot queries or empty results

---

## 📦 Requirements

- Python
- [Amadeus API key](https://developers.amadeus.com/register)

Install dependencies:

```bash
pip install amadeus
````

---

## 🔑 Amadeus API Setup

1. Go to [developers.amadeus.com](https://developers.amadeus.com/register) and **create a free account**.
2. After confirming your email, go to your **Dashboard > My Self-Service Workspace**.
3. Create a new application.
4. Copy your:

   * `API Key` (aka `client_id`)
   * `API Secret` (aka `client_secret`)
5. Open the Python file and replace these two lines near the top:

```python
AMADEUS_API_KEY = "your_api_key_here"
AMADEUS_API_SECRET = "your_api_secret_here"
```

> 🔐 Tip: If you plan to publish the project or use it long-term, store your credentials in environment variables or a `.env` file instead of hardcoding them.

---

## 🛫 Usage

Run the script from your terminal:

```bash
python flight_search_tool.py
```

You will be prompted to enter:

* Origin airport code (e.g., `JFK`)
* Destination airport code (e.g., `ATH`)
* Travel date or date range
* Optional stopover (e.g., `LHR`) to simulate manual layovers
* Passenger breakdown:

  * Adults
  * Seniors
  * Students
  * Children under 11 / 17
  * Infants (lap or seat)

The tool will search flights via the Amadeus API and display:

* Airline segments
* Departure & arrival times
* Price in EUR
* **Clickable Kayak link** with correct passenger & date configuration

---

## 📸 Example

```text
🔍 A flight search tool giving best routes and days with the amadeus api and gives Kayak Links

 Created by the one and only tortupouce
Enter origin airport code (e.g., JFK): JFK
Enter destination airport code (e.g., ATH): ATH
Search single date or date range? (S/R): S
Enter departure date (YYYY-MM-DD): 2025-05-26
Enter desired stopover airport code (optional, e.g., LHR):
Number of adults (default = 1):
Number of seniors (default = 0):
Number of students (default = 0):
Infants on lap under 2 (L) (default = 0):
Children under 2 with seat (S) (default = 0):
Children under 11 (default = 0):
Children under 17 (default = 0):

 // direct | Option 1
  A1: JFK → ATH | 2025-05-26T01:15:00 → 2025-05-26T17:30:00
💰 Price: €238.29
🔗 Kayak Link: https://www.kayak.com/flights/JFK-ATH/2025-05-26/1adults
```

---

## 🧠 Notes

* The Amadeus free tier allows **up to 500 flight search API calls per month** (apparently, didn't test).
* If you see `No flight options found`, try:

  * Changing the travel date
  * Reducing passengers
  * Removing the stopover
  * Printing debug info (already included in the script)
* The API returns prices in **EUR** by default. Cause we're not ameritards

---

## 🛠️ Customization Ideas

Want to extend the app? Here are some ideas:

* Export results to CSV or JSON
* Add max price filters or time constraints
* Build a web UI with Flask or Streamlit
* Support return flights
* Integrate with email or Telegram bot for alerts
* Add stayover time
* Impement the flight order from Amadeus but i think it's a pay option, anyway, I'm not doing it
* give this script an actual use

---

## 📝 License

This project is licensed under a [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license.  
You may use, modify, and share the code for **personal and open-source purposes only**.  
**Commercial use is strictly prohibited**.


---

## ✉️ Author

Made by me (tortupouce)

```
