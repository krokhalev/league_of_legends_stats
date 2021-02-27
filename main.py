from config import BOT_TOKEN
from config import RIOT_API
from aiogram import Bot, Dispatcher, executor, types
from riotwatcher import LolWatcher
import re

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

api_key = RIOT_API  # global variables
watcher = LolWatcher(api_key)
my_region = 'euw1'


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Enter your summoner name')


@dp.message_handler()
async def process(message: types.Message):
    user_info = message['from']
    first_name = user_info['first_name']
    identifier = user_info['id']

    if identifier == 76939702:
        await bot.send_message(message.from_user.id, 'Glad to see you, Creator')
    else:
        await bot.send_message(message.from_user.id, f'Glad to see you, {first_name}')

    language = message['text']

    if re.search(r'[а-яА-ЯёЁ]', language):  # fix language problem
        await bot.send_message(message.from_user.id, 'Please, use english')
    else:
        me = watcher.summoner.by_name(my_region, message['text'])
        my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])  # rank status for summoner
        solo_duo = []
        flex = []
        main = []

        if my_ranked_stats == []:
            await bot.send_message(message.from_user.id, 'Sorry, the account is not calibrated')
        else:
            if my_ranked_stats[0]['queueType'] == 'RANKED_FLEX_SR':  # fix substitution problem
                solo_duo_stats = my_ranked_stats[1]
                flex_stats = my_ranked_stats[0]
            else:
                solo_duo_stats = my_ranked_stats[0]
                flex_stats = my_ranked_stats[1]

            for key in solo_duo_stats:  # main status for summoner
                if key == 'summonerName' or key == 'inactive' or key == 'hotStreak':
                    main.append(solo_duo_stats[key])

            main.insert(1, '\n Online:')
            main.insert(3, '(beta)')
            main.insert(4, '\n Hot streak:')
            main.insert(7, '(beta)')
            main1 = ' '.join(map(str, main))

            for key in solo_duo_stats:  # solo duo rank status for summoner
                if key == 'tier' or key == 'rank' or key == 'leaguePoints' or key == 'wins' or key == 'losses':
                    solo_duo.append(solo_duo_stats[key])

            solo_duo_win_rate = round(
                solo_duo_stats['wins'] / ((solo_duo_stats['wins'] + solo_duo_stats['losses']) / 100), 1)

            solo_duo.insert(2, ',')
            solo_duo.insert(4, 'LP')
            solo_duo.insert(5, '\n Wins:')
            solo_duo.insert(7, '\n Losses:')
            solo_duo.extend(('\n Win rate:', solo_duo_win_rate, '%'))
            solo_duo1 = ' '.join(map(str, solo_duo))

            for key in flex_stats:  # flex rank status for summoner
                if key == 'tier' or key == 'rank' or key == 'leaguePoints' or key == 'wins' or key == 'losses':
                    flex.append(flex_stats[key])

            flex_win_rate = round(flex_stats['wins'] / ((flex_stats['wins'] + flex_stats['losses']) / 100), 1)

            flex.insert(2, ',')
            flex.insert(4, 'LP')
            flex.insert(5, '\n Wins:')
            flex.insert(7, '\n Losses:')
            flex.extend(('\n Win rate:', flex_win_rate, '%'))
            flex = ' '.join(map(str, flex))
            await bot.send_message(message.from_user.id, f' Summoner: {main1} \n\nSOLO / DUO STATS:\n '
                                                         f'{solo_duo1} \n\nFLEX STATS:\n {flex}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)