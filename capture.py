import requests
import json
import os
import datetime
import sys


def getCurrentProgram(data):
    if not data or 'Channel Off Air' in data:
        return '', '', '', ''
    time = data.split('<span class="time">')[-1].split('<')[0]
    title = data.split('</h3>')[0].split('>')[-1]
    programLink = baseurl + data.split('<a href="')[-1].split('"')[0]
    img = 'https://' + s.get(programLink).text.split('.jpg')[0].split('https://')[-1] + '.jpg'
    description = raw.split('<p>')[-1].split('</p>')[0]
    if not description:
        description = raw.split('<span class="desc">')[-1].split('</span>')[0]
    if '><' in description:
        description = ''
    return time, title, img, description
    

def getUpcomingPrograms(response, date):
    response = response.split('<li class="ongoing">')[-1]
    #programs = list(map(lambda x:(f"{x.split('<')[0]}", x.split('<h3>')[-1].split('</h3>')[0], x.split('<p>')[-1].split('</p>')[0]), response.split('<span class="time">')[1:]))
    programs = []
    times = ['am']
    for x in response.split('<span class="time">')[1:]:
        time = x.split('<')[0]
        title = x.split('</h3>')[0].split('>')[-1]
        description = x.split('<p>')[-1].split('</p>')[0]
        if not description:
            description = x.split('<span class="desc">')[-1].split('</span>')[0]
        if '><' in description:
            description = ''

        if 'pm' in times[-1] and 'am' in time:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            date += datetime.timedelta(days=1)
            date = datetime.datetime.strftime(date, '%Y-%m-%d')
        times.append(time)

        time = f'{date} {time}'
        
        if (time, title, description) not in programs:
            programs.append((time, title, description))
    return programs
    
    
if __name__ == '__main__':
    s = requests.session()
    with open('channelList.json') as channelList:
        channels = json.load(channelList)
    # for testing

    """
    channels = {
    #    'Sky News': 'sky-news',
    #    "BBC One London": "bbc-one-london",
    #    'Tiny Pop (Freeview) Today': 'tiny-pop-freeview'
        }
    """
    
    baseurl = 'https://tv24.co.uk'
    today = datetime.datetime.strftime(datetime.datetime.now(datetime.UTC), '%Y-%m-%d')
    if 'files' not in os.listdir():
        os.mkdir('files')
    os.chdir('files')
    total_channels = len(channels)
    count = 0
    for channel in channels:
        count += 1
        print(f'[+] Getting tv guide for {channel}... [{count}/{total_channels}]')
        ch_name = channels[channel]
        img, title, description = 'NA', 'NA', 'NA'
        try:
            response = s.get(f'{baseurl}/x/channel/{ch_name}/000/{today}').text
            raw = response.split('<li class="ongoing">')[-1].split('</li>')[0]
            time, title, img, description = getCurrentProgram(raw)
            currentProgram = f'{time} - {title}\n{description}'
        except Exception as e:
            print(f'some error: {e}')

        # Create folder if not already present
        if ch_name not in os.listdir():
            os.mkdir(ch_name)

        # Writing current program details
        with open(f'{ch_name}/current_program.txt', 'w') as writer:
            writer.write(f'{currentProgram}')

        # Writing current program title
        with open(f'{ch_name}/current_program_title.txt', 'w') as writer:
            writer.write(f'{title}')

        # Writing current program image link
        with open(f'{ch_name}/current_program_image.txt', 'w') as writer:
            writer.write(f'{img}')
        if img:
            img_response = s.get(img)
            with open(f'{ch_name}/current_program_image.jpg', 'wb') as file:
                file.write(img_response.content)

        # Writing now-and-next programs details
        next_x_days = 7
        upcoming_programs_list = []
        for day in range(next_x_days):
            date = datetime.datetime.strftime(datetime.datetime.now(datetime.UTC)+datetime.timedelta(days=day), '%Y-%m-%d')
            nextDayResponse = s.get(f'{baseurl}/x/channel/{ch_name}/000/{date}').text
            upcoming_programs_list += getUpcomingPrograms(nextDayResponse, date)
        upcoming_programs_sorted = []
        for program in upcoming_programs_list:
            if program not in upcoming_programs_sorted:
                upcoming_programs_sorted.append(program)

        upcoming = ''
        for program in upcoming_programs_sorted:
            for line in program:
                upcoming += f'{line}\n'
            upcoming += '\n'
        
        with open(f'{ch_name}/current_and_upcoming.txt', 'w') as writer:
            writer.write(f'{upcoming}')
        print(f'[*] {channel}\n{time} - {title}\n{description}\n')
