from .config import VIP_COST, VERSION

payment_message = 'Покупка Vip на месяц \nID - <code><b>{0}</b></code>\n' \
                  f'Сумма платежа - <b>{VIP_COST} руб.</b>\n' \
                  'Статус платежа - {1}'

help_message = 'ℹ️ Информация о боте:\n' \
               f'🔧 Версия бота: {VERSION}v\n' \
               '<i>Если вас интересует заказ бота под ключ, то пишите @Proksima1</i>'

search_steam_id_error = '🔧В работе бота возникли технические неполадки, пожалуйста, повторите попытку позже!'
steam_id_not_found = "Такого steam_id не найдено, попробуйте ввести другой."
vip_set = 'VIP-статус выдан ;) Приятной игры!'
