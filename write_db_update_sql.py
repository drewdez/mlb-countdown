import json, pytz, re, time
from datetime import datetime
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver

CALENDAR_CONTENT = SoupStrainer('div', {'class': 'list-mode'})
TZ_CONTENT = SoupStrainer('div', {'class': 'timezone-note above-legend'})
TZ_DICT = {
    'PT': pytz.timezone('US/Pacific'),
    'MST': pytz.timezone('US/Arizona'),
    'MT': pytz.timezone('US/Mountain'),
    'CT': pytz.timezone('US/Central'),
    'ET': pytz.timezone('US/Eastern'),
    'cactus': pytz.timezone('US/Arizona'),
    'grapefruit': pytz.timezone('US/Eastern')
}

def main():
    with open('team_data.json') as data_file:
        teams_json = json.load(data_file)
    teams = teams_json['teams']
    output_file = 'populate_db_{}.sql'.format(datetime.now().strftime('%Y'))
    write_sql_header(output_file)
    driver = webdriver.Firefox()

    for team in teams:
        month = 2
        while month < 5 and (not 'pc_date' in team or not 'ex_date' in team or not 'rs_date' in team):
            sched_url = 'https://www.mlb.com/{}/schedule/{}-0{}/list'.format(team['sched_id'], datetime.now().strftime('%Y'), month)
            driver.get(sched_url)
            time.sleep(30)
            sched_html = driver.page_source
            soup = BeautifulSoup(sched_html, 'html.parser', parse_only = CALENDAR_CONTENT)
            tz_element = BeautifulSoup(sched_html, 'html.parser', parse_only = TZ_CONTENT)
            if not 'timezone' in team:
                team['timezone'] = get_tz_from_timezone_note(tz_element, team['id'])
                print team['id'], 'time zone:', team['timezone'].zone
            if not 'pc_date' in team:
                pc_element = soup.find(class_='non-game-event-title', text=re.compile("[Pp]itchers and [Cc]atchers"))
                if pc_element:
                    team['pc_date'] = get_datetime_from_non_game_event(pc_element.parent.parent.parent, TZ_DICT[team['st_league']])
                    print team['id'], 'pitchers and catchers report:', team['pc_date']
            if not 'ex_date' in team:
                ex_element = soup.find(class_='game-type-note', text='Spring Training')
                if ex_element:
                    team['ex_date'] = get_datetime_from_game(ex_element.parent.parent, team['timezone'])
                    print team['id'], 'exhibition opener:', team['ex_date']
            if not 'rs_date' in team:
                rs_element = soup.find(class_='game-type-note', text='Reg. season')
                if rs_element:
                    team['rs_date'] = get_datetime_from_game(rs_element.parent.parent, team['timezone'])
                    print team['id'], 'regular season opener:', team['rs_date']
            month += 1
        write_sql_line(output_file, team)
    driver.close()
    driver.quit()

def write_sql_header(output_file):
    sql_header = '''\
drop table if exists Dates;
create table Dates (
    teamAbbr text primary key,
    teamFull text not null,
    teamNickname text not null,
    pcReport text not null,
    exOpener text not null,
    rsOpener text not null,
    background_color text not null,
    text_color text not null
);

'''

    with open(output_file, 'w') as output_file:
        output_file.write(sql_header)

def write_sql_line(output_file, team):
    team_string = "insert into Dates values ('{}');\n".format(
        "', '".join((team['id'], team['full_name'], team['nickname'],
        team['pc_date'], team['ex_date'], team['rs_date'],
        team['background_color'], team['text_color'])))
    with open(output_file, 'a') as output_file:
        output_file.write(team_string)

def get_tz_from_timezone_note(tz_note, team_id):
    tz_string = re.match(r"^All [Tt]imes (\w+) unless otherwise noted.", tz_note.get_text(strip=True)).group(1)
    if team_id == 'ARI': tz_string = 'MST'
    return TZ_DICT[tz_string]

def get_datetime_from_game(game, tz):
    date_string = re.match(r"(\w{3} \d{2})", game.find(class_='month-date').get_text()).group(1)
    time_string = re.match(r"^(\d+:\d{2} \wm) (\w{3})", game.find(class_='primary-time').get_text(strip=True)).group(1).upper()
    local = datetime.strptime(date_string + ' ' + datetime.now().strftime('%Y') + ' ' + time_string, '%b %d %Y %I:%M %p')
    return tz.localize(local).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def get_datetime_from_non_game_event(event, tz):
    date_string = re.match(r"(\w{3} \d{2})", event.find(class_='month-date').get_text()).group(1)
    local = datetime.strptime(date_string + ' ' + datetime.now().strftime('%Y') + ' 08:00 AM', '%b %d %Y %I:%M %p')
    return tz.localize(local).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

if __name__ == '__main__':
    main()
