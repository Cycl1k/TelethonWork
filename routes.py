from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    jsonify,
    request,
    send_file
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from flask_qrcode import QRcode
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from telethon import TelegramClient, sync, events
from telethon.utils import get_display_name

import asyncio
import configparser
import os.path

from app import create_app,db,login_manager,bcrypt
from models import User
from forms import login_form,register_form
from wb import wb_items

#Получаем данные из конфига
config = configparser.ConfigParser()
config.read('config.ini')

#Данные от Telegram API
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()
qrcode = QRcode(app)

#Время жизни сессии в AFK
@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    asyncio.set_event_loop(asyncio.new_event_loop())
    return render_template("index.html",title="Home")

#Логин, через web
@app.route("/loginn/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )

#Регистрация в системе
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

#Выход из системы
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Авторизация в Web-клиенте
@app.route('/tg', methods = ("GET", "POST"), strict_slashes=False)
def tg():
    try:
        username = current_user.username

        token = token_generation(username)

        return render_template('tg.html',title="Telegram", h = token)
    except AttributeError:
        return redirect(url_for('login'))

#Генератор токена для QR кода
def token_generation(username_session):
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = TelegramClient(username_session, api_id, api_hash)
    client.connect()
    qr = client.qr_login()
    token = qr.url
    client.disconnect()
    return token

#QR код для API
@app.route('/login', methods = ["POST"])
def login_api():
    username_session = request.json['phone']

    token = token_generation(username_session)

    return jsonify({
        'qr_link_url': 'http://127.0.0.1:5000/qrcode?data=' + token
        })

#Генератор картинки с QR-кодом
@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")

#Базовая информация об УЗ Телеграмма
@app.route('/get_me', methods = ("GET", "POST"), strict_slashes=False)
def get_me():
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    try:
        username = current_user.username

        client = TelegramClient(username, api_id, api_hash)
        client.connect()

        me_info = client.get_me()
        me_info = me_info.first_name + ' ' + me_info.last_name + '->' + me_info.username

        client.disconnect()

        return render_template('get_me.html',title="Telegram", h = me_info)
    except AttributeError:
        return redirect(url_for('login'))
    except TypeError:
        client.disconnect()
        return redirect(url_for('login'))
    except:
        client.disconnect()
        return redirect(url_for('login'))

#Переписка
@app.route('/chats', methods = ("GET", "POST"), strict_slashes=False)
def chat_face():
    asyncio.set_event_loop(asyncio.new_event_loop())
    username = current_user.username

    if request.method == 'POST':
        
        client = TelegramClient(username, api_id, api_hash)

        user_sender = request.args.get('data', '')

        ffff = request.form['send_message']
        client.connect()
        client.send_message(user_sender, ffff)
        client.disconnect()
        return redirect(url_for('chat_tg'))
    else:
        try:
            chat_name = request.args.get("data", "")

            messList = chat_histary(username, chat_name)
            return render_template('tg_chats.html', chat = messList.items(), to_user = chat_name)
        except:
            client.disconnect()
            return redirect(url_for('chat_tg'))

@app.route('/messages', methods = ["GET", "POST"])
def chat_histary_API():
    
    phone = request.args.get("phone","")
    uname = request.args.get("uname","")

    if request.method == 'POST':
        status = send_message()
        return jsonify({
            'status': status
        })
    else:
        messList = chat_histary(phone, uname)
        return jsonify({
            'messages': messList
        })

def chat_histary(username, uname):
    asyncio.set_event_loop(asyncio.new_event_loop())

    client = TelegramClient(username, api_id, api_hash)
    client.connect()
    messList = {}
    counet = 0
    found_media = {}
    
    me_acc = client.get_me()
    messages = client.get_messages(uname, limit=50)
    client.disconnect()

    for msg in reversed(messages):
        uname = get_display_name(msg.sender)

        #Тип сообщения
        if getattr(msg, 'media', None):
            found_media[msg.id] = msg
            content = '{}'.format(
                type(msg.media).__name__)

        elif hasattr(msg, 'message'):
            content = msg.message
        elif hasattr(msg, 'action'):
            content = str(msg.action)
        else:
            # В остальных случаях
            content = type(msg).__name__

        #Проверка, что мы отправили это сообщение
        if msg.sender.first_name + msg.sender.last_name == me_acc.first_name + me_acc.last_name :
                isSelf = True
        else:
                isSelf = False

        messList.update(
            {counet:
            {
                'name': uname,
                'is_self': isSelf,
                'message' : content
            }
        })
        counet+=1
    
    return messList

def send_message():
    asyncio.set_event_loop(asyncio.new_event_loop())

    message_text = request.json['message_text']
    phone = request.json['from_phone']
    username = request.json['username']

    client = TelegramClient(phone, api_id, api_hash)
    client.connect()

    try:
        client.send_message(username, message_text)
        client.disconnect()
        return 'ok'
    except ValueError:
        client.disconnect()
        return 'error+'
    except:
        client.disconnect()
        return 'error'


#Список доступных чатов (групповые и личные)
@app.route('/chat', methods = ("GET", "POST"), strict_slashes=False)
def chat_tg():

    asyncio.set_event_loop(asyncio.new_event_loop())
    try:
        username = current_user.username
        client = TelegramClient(username, api_id, api_hash)
        client.connect()
        chat_name = client.get_dialogs()
        client.disconnect()
        dict_dialog = {}
        counter = 0

        for x in chat_name:
            name_id = ''
            type_chat_str = str(x.entity).split('(')[0]
            
            if type_chat_str == 'Chat':
                type_chat = type_chat_str
                name_id = str(x.name)
                if ' ' in name_id:
                    name_id = name_id.replace(' ', '%20')
                else:
                    name_id = x.name
            elif type_chat_str == 'User':
                type_chat = type_chat_str
                name_id = x.entity.username
                if name_id == 'None':
                    name_id = get_display_name(x.entity.id)

            if name_id != '' and x.name != '':
                dict_dialog.update(
                    {
                        counter:
                        {
                            'name' : x.name,
                            'type': type_chat,
                            'hhh': name_id
                        }
                    }
                )
                counter +=1

        
        chat_name = dict_dialog
        return render_template('tg_chat.html', chat = chat_name.items())
    except:
        client.disconnect()
        return redirect(url_for('get_me'))


@app.route('/check/login', methods=['GET'])
def check_login():

    asyncio.set_event_loop(asyncio.new_event_loop())

    username = request.args.get('phone', '')

    

    file_check = username + '.session'
    if os.path.isfile(file_check) == True:
        try:
            client = TelegramClient(username, api_id, api_hash)
            client.connect()
            f = client.get_me()
            client.disconnect()
            if f != None:
                result_check = 'logined '
            else:
                result_check = 'waiting_qr_login'
        except:
            client.disconnect()
            result_check = 'error'
    else:
        result_check = 'error'
    return jsonify(result_check)

@app.route('/wb', methods = ("GET", "POST"), strict_slashes=False)
def wb_item():
    item_name = request.args.get('wild','')
    wb_list = wb_items(item_name)
    if request.method == 'GET':
        
        return render_template('wb.html', wb_list = wb_list)
    else:
        return wb_list

if __name__ == "__main__":
    app.run(debug=True)
