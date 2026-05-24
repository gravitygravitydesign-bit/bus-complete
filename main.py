import flet as ft
import random
import string
import firebase_admin
from firebase_admin import db, credentials
import time

# --- إعدادات Firebase ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://gravitybusgame-default-rtdb.europe-west1.firebasedatabase.app'
        })
except Exception as e:
    print(f"Firebase Error: {e}")

def main(page: ft.Page):
    #page.title = "اتوبيس كومبليت - Gravity Projects"
    #page.theme_mode = ft.ThemeMode.DARK
    #page.rtl = True 
    #page.padding = 20
    #page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # اجبر الصفحة كاملة والاتجاهات والنصوص تكون من اليمين للشمال كوضع افتراضي
    page.rtl = True
    page.locale = "ar-EG"  # تحديد اللغة العربية كمان بيظبط المحاذاة التلقائية للمتصفح
    
    # إدارة الجلسة والمستمعين
    session = {
        "room_id": "", 
        "team_id": "", 
        "team_name": "", 
        "is_in_game": False, 
        "review_started": False, 
        "timer_started": False,
        "current_listener": None 
    }

    def stop_listener():
        """دالة لإيقاف أي مستمع نشط"""
        if session["current_listener"]:
            try:
                session["current_listener"].close()
                session["current_listener"] = None
            except:
                pass

    def show_main_menu():
        stop_listener()
        page.clean()

        # 1. الخلفية المتحركة (الكلمة مدمجة بداخلها الآن)
        bg_image = ft.Image(
            src="bg.gif", # تأكد أن الـ GIF الجديد يحتوي على الاسم
            fit="cover",
            width=page.width, 
            height=page.height,
        )

        # 2. محتوى القائمة (الزراير فقط)
        menu_content = ft.Container(
            content=ft.Column([
                # زودنا المسافة شوية عشان الزراير متنزلش تحت أوي لو الكلمة واخدة مساحة في الـ GIF
                ft.Divider(height=100, color="transparent"),
                
                ft.FilledButton(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED), ft.Text("يلا بينا", size=22, weight="bold")],
                        alignment="center",
                    ),
                    width=320,
                    height=70,
                    style=ft.ButtonStyle(
                        # جرب اللون الـ Deep Orange ده هيكون تحفة مع اللوجو بتاعك
                        bgcolor=ft.Colors.RED_700, 
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=20), # خليته دائري أكتر شوية
                    ),
                    on_click=lambda _: show_multiplayer_selection(),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            expand=True,
        )

        # 3. تجميع الطبقات
        page.add(
            ft.Stack([
                bg_image,
                menu_content
            ], expand=True)
        )
        
        page.update()
        
    def show_multiplayer_selection():
        page.clean()

        # 1. نفس الخلفية عشان اللعبة تبقى متناسقة
        bg_image = ft.Image(
            src="bg2.gif", # أو bg.jpg حسب اللي استقريت عليه
            fit="cover",
            width=page.width, 
            height=page.height,
        )

        # 2. محتوى الصفحة (الزراير)
        menu_content = ft.Container(
            content=ft.Column([
                # عنوان الصفحة
                #ft.Text("تجهيز الغرفة", size=30, weight="bold", color="black"),
                #ft.Divider(height=20, color="transparent"),

                # زرار إنشاء غرفة
                ft.FilledButton(
                    content=ft.Text("إنشاء غرفة جديدة", size=20, weight="bold"),
                    width=320,
                    height=60,
                    style=ft.ButtonStyle(
                        bgcolor="red", # لون أزرق صريح وجامد
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                    on_click=lambda _: show_create_room_settings()
                ),

                ft.Divider(height=3, color="transparent"),

                # زرار دخول غرفة
                ft.FilledButton(
                    content=ft.Text("دخول غرفة مع فريق", size=20, weight="bold"),
                    width=320,
                    height=60,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLACK, # لون برتقالي/ذهبي فخم
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=15),
                    ),
                    on_click=lambda _: show_join_room_ui()
                ),

                ft.Divider(height=20, color="transparent"),

                # زرار الرجوع بشكل أشيك
                #ft.TextButton(
                    #content=ft.Text("رجوع للقائمة الرئيسية", size=18, weight="bold", color="black"),
                    #on_click=lambda _: show_main_menu()
                #)

            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, # ده اللي هيخليهم في نص العرض
            alignment=ft.MainAxisAlignment.CENTER # ده اللي هيخليهم في نص الطول
            ),
            expand=True,
        )

        # إضافة الطبقات
        page.add(
            ft.Stack([
                bg_image,
                menu_content
            ], expand=True)
        )
        page.update()

    def show_create_room_settings():
        page.clean()
        
        # 2. جعل نص الدروب داون Bold
        num_teams_input = ft.Dropdown(
            label="عدد الفرق",
            value="2",
            width=250,
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.WHITE), 
            text_style=ft.TextStyle(weight="bold", size=18, color="black"),
            options=[
                ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4"),
                ft.dropdown.Option("5"),
                ft.dropdown.Option("6"),
                #ft.dropdown.Option("7"),
                #ft.dropdown.Option("8"),
                #ft.dropdown.Option("9"),
                #ft.dropdown.Option("10"),
            ],
            border_color="red",
        )

        # 1. عدل الـ Slider وخلي الـ step واضح بـ 1
        num_qs_input = ft.Slider(
            min=1, 
            max=10, 
            divisions=9,  # من 1 لـ 10 محتاجين 9 تقسيمات بالظبط عشان يمشي (1, 2, 3...)
            label="عدد الجولات: {value}",
            value=5,
            width=250,
            active_color=ft.Colors.RED_ACCENT_700,
            thumb_color=ft.Colors.RED_900,
        )

        # 2. لما تيجي تقرأ القيمة في الكود، اقرأها كدة:
        total_rounds = int(round(num_qs_input.value))

        def proceed_to_names(e):
            n = int(num_teams_input.value)
            qs = int(num_qs_input.value)
            show_naming_screen(n, qs)

        page.add(
            ft.Stack(
                [
                    ft.Image(
                        src="bg2.gif",
                        fit="cover", 
                        width=page.width,
                        height=page.height,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                #ft.Text("إعدادات الغرفة", size=35, weight="bold", color="blue"),
                                
                                # 1. نزلنا المربع تحت بزيادة مسافة الـ Divider
                                ft.Divider(height=20, color="transparent"), 
                                
                                num_teams_input,
                                ft.Text("حدد عدد الجولات", size=16, color="red", weight="bold"),
                                num_qs_input,
                                ft.Divider(height=1, color="transparent"),
                                
                                # 3 & 4. تغيير لون الزرار وجعل النص Bold
                                ft.FilledButton(
                                    content=ft.Text("يلا نسمي الفرق", size=18, weight="bold"), # نص Bold
                                    on_click=proceed_to_names,
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.Colors.RED_800, # تغيير لون الزرار
                                        color=ft.Colors.WHITE,
                                        shape=ft.RoundedRectangleBorder(radius=15)
                                    ),
                                    width=220,
                                    height=55
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.Alignment(0, 0), 
                        expand=True,
                    ),
                ],
                expand=True,
            )
        )
        page.update()
        
    def show_naming_screen(num_teams, num_rounds):
        page.clean()
        
        team_inputs = []
        for i in range(num_teams):
            team_inputs.append(
                ft.TextField(
                    label=f"اسم الفريق {i+1}",
                    width=280,
                    bgcolor=ft.Colors.WHITE,
                    text_style=ft.TextStyle(weight="bold", color="red"),
                    border_color="red",
                    border_radius=15,
                    focused_border_color="orange",
                )
            )

        def create_room_and_start(e):
            room_id = str(random.randint(100, 999))
            players_data = {}
            alphabet = list(string.ascii_uppercase)
            used_codes = [room_id]
            
            for i in range(num_teams):
                t_letter = alphabet[i]
                if i == 0:
                    entry_code = room_id  
                else:
                    while True:
                        rand_code = str(random.randint(100, 999))
                        if rand_code not in used_codes:
                            entry_code = rand_code
                            used_codes.append(rand_code)
                            break
                
                players_data[t_letter] = {
                    "name": team_inputs[i].value if team_inputs[i].value else f"فريق {t_letter}",
                    "joined": True if i == 0 else False,
                    "ready": False,
                    "score": 0,
                    "entry_code": entry_code  
                }

            db.reference(f'Rooms/{room_id}').set({
                "settings": {
                    "num_teams": num_teams,
                    "num_questions": num_rounds
                },
                "players": players_data,
                "status": "waiting",
                "current_round": 1,
                "stop_pressed": False
            })

            # === تعديل سحري: الأدمن معرفه الثابت هو A لمنع الانقسام ===
            session.update({
                "room_id": room_id,
                "team_id": "A",
                "team_name": team_inputs[0].value if team_inputs[0].value else "الأبطال",
                "is_in_game": False
            })

            show_room_lobby()

        page.add(
            ft.Stack([
                ft.Image(src="bg2.gif", fit="cover", width=page.width, height=page.height),
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=2, color="transparent"),
                        ft.Container(
                            content=ft.Column(team_inputs, spacing=15, horizontal_alignment="center"),
                            padding=20,
                            bgcolor=ft.Colors.with_opacity(0.6, "white"),
                            border_radius=20,
                        ),
                        ft.Divider(height=1, color="transparent"),
                        ft.FilledButton(
                            content=ft.Text("يلا بينــا", size=22, weight="bold"),
                            on_click=create_room_and_start,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=15)),
                            width=200, height=55
                        ),
                    ], horizontal_alignment="center", alignment="center"),
                    alignment=ft.Alignment(0, -0.2), expand=True,
                ),
            ], expand=True)
        )
        page.update()
        
    def show_room_lobby():
        stop_listener()
        page.clean()
        
        # حماية إضافية لتأكيد توحيد معرف الأدمن
        if session["team_id"] == "Team_A":
            session["team_id"] = "A"

        room_id = session["room_id"]
        team_id = session["team_id"]
        team_name = session.get("team_name", "الفريق")
        session["is_in_game"] = False 
        session["timer_started"] = False

        header_info = ft.Container(
            content=ft.Column([
                ft.Text(f"👋 يا مرحب بـ {team_name}", size=22, weight="bold", color=ft.Colors.AMBER_400),
                ft.Text("مستنين باقي الفرق تستعد 🤌", size=14, color=ft.Colors.WHITE70),
            ], horizontal_alignment="center", spacing=5),
            margin=ft.Margin(0, 0, 0, 20) 
        )
        
        codes_container = ft.Column(spacing=8, horizontal_alignment="center")
        players_container = ft.Column(spacing=12)

        room_data = db.reference(f'Rooms/{room_id}').get()
        
        # تحديد إجمالي عدد الفرق المطلوبة للغرفة من الإعدادات
        total_expected_teams = int(room_data['settings']['num_teams']) if room_data else 1
        
        # توليد وعرض الأكواد العشوائية للأدمن (A) فقط
        if team_id == "A" and room_data:
            if total_expected_teams > 1:
                codes_container.controls.append(
                    ft.Text("أكواد دخول الفرق التانيه :", color="amber", weight="bold", size=16)
                )
                alphabet = list(string.ascii_uppercase)
                grid = ft.Row(wrap=True, alignment="center", spacing=10)
                
                for i in range(1, total_expected_teams):
                    t_letter = alphabet[i]
                    team_info = room_data.get('players', {}).get(t_letter, {})
                    display_name = team_info.get('name', f"فريق {t_letter}")
                    specific_code = team_info.get('entry_code', "000")
                    
                    grid.controls.append(
                        ft.Container(
                            content=ft.Text(f"{display_name} : {specific_code}", color="white", weight="500", size=15),
                            bgcolor="white10", padding=10, border_radius=8, border=ft.Border.all(1, "white24")
                        )
                    )
                codes_container.controls.append(grid)

        # زر البداية للأدمن
        start_btn = ft.FilledButton(
            content=ft.Text("🚍  إبدأ الجولة دلوقتي  🚍", size=20, weight="bold"),
            disabled=True,
            on_click=lambda _: start_game_logic(), 
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DISABLED: ft.Colors.GREY_700, ft.ControlState.DEFAULT: ft.Colors.RED_900},
                color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=12),
            ),
            width=300, height=55,
        )

        def start_game_logic():
            letters = ["أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"]
            all_cats = ["ولد", "بنت", "جماد", "حيوان", "نبات", "بلاد", "وظيفة", "فيلم", "مسلسل", "فنان"]
            selected_cats = random.sample(all_cats, 5)
            db.reference(f'Rooms/{room_id}').update({
                'status': 'timer',
                'current_letter': random.choice(letters),
                'selected_cats': selected_cats,
                'stop_pressed': False,
                'round_scores': {}
            })

        ready_btn = ft.ElevatedButton(
            content=ft.Text("فريقنا جاهز 💪🏻", color="white", size=16, weight="bold"),
            on_click=lambda _: db.reference(f'Rooms/{room_id}/players/{team_id}').update({'ready': True}),
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10)),
            height=50, width=200
        )

        def stream_handler(message):
            data = db.reference(f'Rooms/{room_id}').get()
            if not data: return
            
            if data.get('status') == 'timer' and not session.get("timer_started"):
                session["timer_started"] = True
                stop_listener()
                show_timer_screen(data.get('current_letter'), data.get('selected_cats'))
                return

            players = data.get('players', {})
            players_container.controls.clear()
            
            # ─── [الـتـعـديـل الـجـوهـري هـنـا لـحـمـايـة الـلـوجـيـك] ───
            all_ready = True
            joined_count = 0  # عداد عشان نضمن إن العدد الفعلي للفرق اكتمل جوه الروم
            
            for t_id, t_info in players.items():
                is_ready = t_info.get('ready', False)
                is_joined = t_info.get('joined', False)
                
                if is_joined:
                    joined_count += 1
                
                # الشرط الصح: لو الفريق مش متصل "أو" متصل بس لسه مش جاهز، يبقى اللعبة متنفعش تبدأ
                if not is_joined or not is_ready: 
                    all_ready = False
                
                display_team_name = t_info.get('name', f"فريق {t_id}")
                
                status_color = ft.Colors.GREEN_ACCENT_400 if is_ready else (ft.Colors.BLUE_400 if is_joined else ft.Colors.GREY_500)
                status_text = "الفريق دلوقتي بأه جاهز      🤫" if is_ready else ("الفريق متصل      😀" if is_joined else "الفريق لسه مدخلش أصلاً  🙄")
                
                players_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON_ROUNDED, color=status_color, size=30),
                            ft.Column([
                                ft.Text(display_team_name, size=18, weight="bold", color="white"),
                                ft.Text(status_text, size=14, color=status_color),
                            ], spacing=2, expand=True),
                            ft.Icon(ft.Icons.CIRCLE, color=status_color, size=12) if is_joined else ft.Container()
                        ]),
                        padding=15, bgcolor="white10", border_radius=15, border=ft.Border.all(1, "white10")
                    )
                )
            
            # تأكيد إضافي: الزرار يتفعل لو كله جاهز وعدد الفرق المتصلة بيساوي نفس عدد الغرفة المختار
            if team_id == "A":
                if all_ready and joined_count == total_expected_teams:
                    start_btn.disabled = False
                else:
                    start_btn.disabled = True
                    
            page.update()

        stop_listener()
        session["current_listener"] = db.reference(f'Rooms/{room_id}').listen(stream_handler)
        
        page.add(
            ft.Container(
                content=ft.Column([
                    header_info,
                    codes_container if team_id == "A" else ft.Container(), 
                    ft.Divider(height=20, color="white24"),
                    ft.Text("قائمة الفرق المتنافسة", size=20, weight="bold", color="orange"),
                    players_container,
                    ft.Divider(height=20, color="transparent"),
                    ft.Row([ready_btn], alignment="center"),
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([start_btn], alignment="center") if team_id == "A" else ft.Container(),
                ], scroll=ft.ScrollMode.ADAPTIVE, horizontal_alignment="center"),
                expand=True, padding=25, 
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                    colors=[ft.Colors.BLUE_GREY_900, ft.Colors.BLACK],
                )
            )
        )
        page.update()
        
    def show_timer_screen(letter, cats):
        page.clean()
        
        # تفعيل اتجاه اليمين للشمال للشاشة بالكامل
        page.rtl = True 
        
        # 1. تعريف نص العداد المنسنتر بالملي بدون ارتفاع وهمي
        countdown_text = ft.Text(
            "5", 
            size=75, 
            weight="bold", 
            color=ft.Colors.WHITE,
            style=ft.TextStyle(height=1.0)
        )
        
        # 2. حلبة العداد الملكية (دائرة سوداء داكنة بحواف ذهبية متوهجة)
        countdown_circle = ft.Container(
            content=ft.Container(
                content=countdown_text, 
                alignment=ft.Alignment(0, 0),
            ),
            alignment=ft.Alignment(0, 0),
            width=140,
            height=140,
            shape=ft.BoxShape.CIRCLE,
            bgcolor="#0a0f12", # أسود داكن ليعطي عمق للرقم
            border=ft.Border.all(4, ft.Colors.AMBER_ACCENT_400), # حواف ذهبية
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.35, ft.Colors.AMBER_400), # توهج ذهبي خفيف
                offset=ft.Offset(0, 6)
            )
        )
        
        # رسالة التنبيه الحماسية تحت العداد
        status_text = ft.Text("اجهزوا واستعدوا.. الجولة هتبدأ حالا 🔥", size=20, weight="bold", color=ft.Colors.WHITE)

        # إضافة العناصر للواجهة بالثيم الداكن المتناسق مع اللعبة
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("🚍 أتوبيس كومبليت 🚍", size=26, weight="bold", color=ft.Colors.WHITE),
                    ft.Divider(height=30, color="white10"),
                    
                    countdown_circle, # هنا حطينا الدائرة الملكية الجديدة مكان الرقم القديم 🚀
                    
                    ft.Container(height=15), # مسافة منسقة
                    status_text,
                    ft.Text("ورونا مين أسرع واحد هايقفل الأتوبيس", size=13, color=ft.Colors.WHITE30)
                ], horizontal_alignment="center", alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
                padding=20,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                    colors=[ft.Colors.BLUE_GREY_900, ft.Colors.BLACK],
                )
            )
        )
        page.update()

        # تشغيل العداد التنازلي البرمجي المستقر (من 5 إلى 1)
        import time
        for i in range(5, 0, -1):
            countdown_text.value = str(i)
            page.update()
            time.sleep(1)
            
        # بعد انتهاء الـ 5 ثواني.. ننقل فوراً لشاشة اللعب
        show_game_screen(letter, cats)

    def show_game_screen(letter, cats):
        if session["is_in_game"]: return 
        session["is_in_game"] = True
        session["review_started"] = False 
        page.clean()
        
        # تفعيل اتجاه الكتابة من اليمين للشمال للشاشة بالكامل
        page.rtl = True 
        
        room_id, team_id = session["room_id"], session["team_id"]
        
        # ─── [الـتـعـديـل الـجـديـد: جلب بيانات الجولات وشريط التقدم] ────────────────
        room_data = db.reference(f'Rooms/{room_id}').get()
        current_round = room_data.get('current_round', 1) if room_data else 1
        total_rounds = room_data.get('settings', {}).get('num_questions', 5) if room_data else 5
        
        # حساب نسبة التقدم للشريط (بين 0.0 و 1.0)
        progress_value = current_round / total_rounds

        progress_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"الجولة {current_round} من {total_rounds}", size=14, color=ft.Colors.AMBER_200, weight="bold"),
                    ft.Icon(ft.Icons.FLAG_ROUNDED, color=ft.Colors.AMBER_400, size=16)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                
                ft.ProgressBar(
                    value=progress_value,
                    width=280,
                    height=6,
                    color=ft.Colors.AMBER_ACCENT_400, # تحميل ذهبي متناسق
                    bgcolor="#141f26",
                )
            ], horizontal_alignment="center", spacing=5),
            margin=ft.Margin(0, 0, 0, 10) # مسافة تحت الشريط لتفصله عن الحرف
        )
        # ─────────────────────────────────────────────────────────────────────────

        # تصميم هيدر يعرض الحرف بشكل ضخم ومبهر
        letter_display = ft.Container(
            content=ft.Column([
                # النص الجديد اللي فوق الدائرة
                ft.Text(
                    "الحرف المطلوب", 
                    size=17, 
                    color=ft.Colors.AMBER_200, 
                    weight="bold"
                ),
                
                # دائرة الحرف الملكية
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(
                            letter, 
                            size=45, 
                            weight="bold", 
                            color=ft.Colors.WHITE,
                            style=ft.TextStyle(height=1.0) # قفل الارتفاع الافتراضي للخط لمنع النزول
                        ),
                        alignment=ft.Alignment(0, 0), # سنترة داخلية إضافية وقاطعة
                    ),
                    alignment=ft.Alignment(0, 0),
                    width=85,
                    height=85,
                    shape=ft.BoxShape.CIRCLE,
                    bgcolor="#0a0f12", 
                    border=ft.Border.all(3, ft.Colors.AMBER_ACCENT_400),
                    shadow=ft.BoxShadow(
                        blur_radius=12,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.AMBER_400),
                        offset=ft.Offset(0, 5)
                    )
                ),
                
                # النص اللي تحت الدائرة
                ft.Text("يلا بسرعه انطلقوووو 🔥", size=12, color=ft.Colors.AMBER_200, weight="w500")
            ], horizontal_alignment="center", spacing=4),
            padding=5,
            alignment=ft.Alignment(0, 0)
        )
        
        # قاموس يربط كل فئة بالإيموجي الخاص بها تلقائياً لزيادة التناسق والمظهر الجمالي
        category_emojis = {
            "ولد": "👦", "بنت": "👧", "جماد": "📦", "حيوان": "🦁", 
            "نبات": "🌱", "بلاد": "🌍", "وظيفة": "💼", "فيلم": "🎬", 
            "مسلسل": "📺", "فنان": "🎭"
        }

        fields = {}
        fields_list = ft.Column(spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
        
        # بناء حقول الإدخال بشكل منسق واحترافي داخل كروت
        for cat in cats:
            emoji = category_emojis.get(cat, "📝")
            tf = ft.TextField(
                hint_text=f"اكتب {cat} يبدأ بـ ({letter})...",
                hint_style=ft.TextStyle(color=ft.Colors.WHITE30, size=14),
                bgcolor="#1e2930",
                border_color="#384f5c",
                border_radius=10,
                focused_border_color=ft.Colors.GREEN_400,
                color=ft.Colors.WHITE,                     
                cursor_color=ft.Colors.GREEN_400,          
                expand=True,
                content_padding=10,
                text_align="right" # محاذاة النص داخل الحقل لليمين
            )
            fields[cat] = tf
            
            # صف يجمع اسم الفئة والإيموجي (يمين) مع حقل الإدخال (يسار) متوافق مع الـ RTL
            fields_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{cat}  {emoji}  :", size=16, weight="bold", color=ft.Colors.WHITE, no_wrap=True),
                        tf
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=8,
                    bgcolor="#141f26",
                    border_radius=12,
                    border=ft.Border.all(1, "#23333e")
                )
            )

        def submit_answers(e):
            current_room = db.reference(f'Rooms/{room_id}').get()
            if current_room and not current_room.get('stop_pressed'):
                answers = {cat: tf.value for cat, tf in fields.items()}
                db.reference(f'Rooms/{room_id}/answers/{team_id}').update(answers)
                db.reference(f'Rooms/{room_id}').update({'stop_pressed': True})

        # زر أتوبيس كومبليت الملكي (Royal Gold)
        stop_btn = ft.Container(
            content=ft.Container(
                content=ft.Text(
                    "🚍    أتوبيس كومبليت    🚍", 
                    size=19, 
                    weight="bold", 
                    color=ft.Colors.AMBER_400,
                    style=ft.TextStyle(height=1.0)
                ),
                alignment=ft.Alignment(0, 0),
            ),
            alignment=ft.Alignment(0, 0),
            width=320, 
            height=58,
            bgcolor="#0a0f12", 
            border_radius=15,
            border=ft.Border.all(2, ft.Colors.AMBER_ACCENT_400), 
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.with_opacity(0.25, ft.Colors.AMBER_400),
                offset=ft.Offset(0, 5)
            ),
            on_click=submit_answers
        )

        def game_monitor(message):
            if session["review_started"]: return
            data = db.reference(f'Rooms/{room_id}').get()
            if data and data.get('stop_pressed'):
                session["review_started"] = True 
                final_answers = {cat: tf.value for cat, tf in fields.items()}
                db.reference(f'Rooms/{room_id}/answers/{team_id}').update(final_answers)
                
                for tf in fields.values(): tf.disabled = True
                
                # تم التعديل هنا ليتوافق مع الـ Container بدلاً من الـ Button
                stop_btn.on_click = None  
                stop_btn.opacity = 0.5   
                page.update()
                
                stop_listener()
                show_review_screen(cats)

        stop_listener()
        session["current_listener"] = db.reference(f'Rooms/{room_id}').listen(game_monitor)

        # عرض شاشة اللعب كاملة بالثيم الداكن المتناسق
        page.add(
            ft.Container(
                content=ft.Column([
                    progress_section, # 🚀 هنا تم إضافة شريط التقدم في أعلى شاشة اللعب 🚀
                    letter_display, 
                    ft.Divider(height=10, color="white10"),
                    ft.Container(content=fields_list, expand=True, padding=ft.Padding(0, 0, 0, 10)),
                    ft.Row([stop_btn], alignment="center")
                ], horizontal_alignment="center"),
                expand=True,
                padding=20,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=[ft.Colors.BLUE_GREY_900, ft.Colors.BLACK],
                )
            )
        )
        page.update()

    def show_review_screen(cats):
        page.clean()
        page.theme_mode = ft.ThemeMode.DARK 
        page.rtl = True 
        
        # تأكيد توحيد المعرفات
        if session["team_id"] == "Team_A":
            session["team_id"] = "A"
            
        room_id, team_id = session["room_id"], session["team_id"]
        is_admin = (team_id == "A")
        
        score_text = ft.Text("مجموع نقاطك : 0", size=22, color=ft.Colors.AMBER_400, weight="bold")
        score_header = ft.Container(
            content=score_text, 
            padding=15, 
            bgcolor="#141f26", 
            border_radius=12,
            alignment=ft.Alignment(0, 0),
            border=ft.Border.all(1, "white10"),
            margin=ft.Margin(0, 0, 0, 15) 
        )
        page.add(score_header)

        review_container = ft.Column(scroll="always", expand=True, spacing=15)
        
        def update_review_ui(message):
            data = db.reference(f'Rooms/{room_id}').get()
            if not data: return
            
            if data.get('status') == 'finished':
                stop_listener()
                show_final_results() 
                return
            
            if data.get('status') == 'waiting':
                stop_listener()
                show_room_lobby()
                return

            my_score = data.get('players', {}).get(team_id, {}).get('score', 0)
            score_text.value = f"مجموع نقاطك : {my_score}"
            
            answers = data.get('answers', {})
            players = data.get('players', {})
            round_scores = data.get('round_scores', {}) 
            
            review_container.controls.clear()
            all_graded = True 
            total_joined = sum(1 for p in players.values() if p.get('joined'))

            for cat in cats:
                cat_col = ft.Column([
                    ft.Text(f"{cat}", size=18, weight="bold", color=ft.Colors.BLUE_400, margin=ft.Margin(0, 10, 0, 0)) 
                ], spacing=10)
                
                cat_grades = round_scores.get(cat, {})
                if len(cat_grades) < total_joined:
                    all_graded = False

                for t_id, t_info in players.items():
                    if not t_info.get('joined'): continue
                    ans = answers.get(t_id, {}).get(cat, "لا يوجد إجابة")
                    current_grade = cat_grades.get(t_id, None)
                    
                    if current_grade is not None:
                        grade_display = f"الدرجة: +{current_grade}"
                        status_color = ft.Colors.GREEN_ACCENT_400
                    else:
                        grade_display = "بانتظار الأدمن ... ⏳"
                        status_color = ft.Colors.AMBER_700
                        
                    grade_view = ft.Text(grade_display, color=status_color, weight="bold", size=14)
                    
                    if is_admin:
                        admin_buttons = ft.Row([
                            ft.ElevatedButton(
                                "10", color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_800,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=ft.Padding(0, 0, 0, 0)),
                                width=50, height=32,
                                on_click=lambda e, t=t_id, c=cat: admin_submit_grade(t, c, 10)
                            ),
                            ft.ElevatedButton(
                                "5", color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_800,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=ft.Padding(0, 0, 0, 0)),
                                width=50, height=32,
                                on_click=lambda e, t=t_id, c=cat: admin_submit_grade(t, c, 5)
                            ),
                            ft.ElevatedButton(
                                "0", color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_800,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6), padding=ft.Padding(0, 0, 0, 0)),
                                width=50, height=32,
                                on_click=lambda e, t=t_id, c=cat: admin_submit_grade(t, c, 0)
                            ),
                        ], spacing=8, visible=(current_grade is None))
                    else:
                        admin_buttons = ft.Container()

                    cat_col.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"👥 {t_info['name']} :", weight="bold", size=15, color=ft.Colors.WHITE),
                                    grade_view
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Divider(height=1, color="white10"),
                                ft.Row([
                                    ft.Text(" الإجابة : ", size=13, color=ft.Colors.WHITE60),
                                    ft.Text(f"\"{ans}\"", size=16, weight="bold", color=ft.Colors.WHITE)
                                ], spacing=8),
                                ft.Row([
                                    ft.Text("نقاط الإجابه : " if current_grade is None else "", size=12, color=ft.Colors.WHITE30),
                                    admin_buttons
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) if is_admin and current_grade is None else ft.Container()
                            ], spacing=10),
                            padding=15, bgcolor="#1e2930", border_radius=12, border=ft.Border.all(1, "#23333e")
                        )
                    )
                review_container.controls.append(cat_col)
            
            if is_admin and all_graded:
                curr_r = int(data.get('current_round', 1))
                total_r = int(data['settings']['num_questions'])
                
                if curr_r < total_r:
                    review_container.controls.append(
                        ft.Container(
                            content=ft.ElevatedButton(
                                f"يلا على الجولة اللي بعدها \"{curr_r+1}\" 🏁", 
                                on_click=lambda _: prepare_next_round(room_id, curr_r + 1),
                                color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_ACCENT_700,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), height=50,
                            ), padding=ft.Padding(10, 0, 10, 0)
                        )
                    )
                else:
                    review_container.controls.append(
                        ft.Container(
                            content=ft.ElevatedButton(
                                "عرض النتائج النهائية 🏆", 
                                on_click=lambda _: db.reference(f'Rooms/{room_id}').update({'status': 'finished'}), 
                                color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)), height=50,
                            ), padding=ft.Padding(10, 0, 10, 0)
                        )
                    )
            page.update()

        def admin_submit_grade(target_t, category, val):
            p_ref = db.reference(f'Rooms/{room_id}/players/{target_t}/score')
            current_val = p_ref.get() or 0
            p_ref.set(current_val + val)
            db.reference(f'Rooms/{room_id}/round_scores/{category}/{target_t}').set(val)

        stop_listener()
        session["current_listener"] = db.reference(f'Rooms/{room_id}').listen(update_review_ui)
        page.add(review_container)
        page.update()

    def prepare_next_round(room_id, next_r):
        updates = {
            'status': 'waiting',
            'current_round': next_r,
            'stop_pressed': False,
            'current_letter': "",
            'answers': {},
            'round_scores': {}
        }
        
        players = db.reference(f'Rooms/{room_id}/players').get()
        if players:
            for p_id in players:
                updates[f'players/{p_id}/ready'] = False

        db.reference(f'Rooms/{room_id}').update(updates)

    def show_final_results():
        stop_listener()
        page.clean()
        room_id = session["room_id"]
        players = db.reference(f'Rooms/{room_id}/players').get() or {}
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('score', 0), reverse=True)
        
        results_list = ft.Column(spacing=15, horizontal_alignment="center")
        results_list.controls.append(ft.Text("النتائج النهائية", size=35, weight="bold", color="amber"))
        
        for i, (t_id, t_info) in enumerate(sorted_players):
            medal = "🥇" if i == 0 else ("🥈" if i == 1 else "🥉")
            results_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(medal, size=30),
                        ft.Text(t_info['name'], size=20, expand=True),
                        ft.Text(f"{t_info.get('score', 0)} نقطة", size=20, weight="bold")
                    ]),
                    padding=15, bgcolor="white10", border_radius=12
                )
            )
        
        page.add(results_list, ft.FilledButton("الرئيسية", on_click=lambda _: show_main_menu()))
        page.update()

    def show_join_room_ui():
        page.clean()
        
        # حقل إدخال الكود الرقمي
        code_in = ft.TextField(
            label="كود الانضمام للغرفه", 
            text_align="center", 
            width=340,
            bgcolor=ft.Colors.WHITE,
            text_style=ft.TextStyle(color="black", weight="bold"),
            border_color="red",
            border_radius=12
        )
        
        def on_join(e):
            val = code_in.value.strip()
            
            # التأكد أن المدخل 3 أرقام فقط
            if len(val) == 3 and val.isdigit():
                # عمل سيرش في كل الغرف النشطة بالفايربيس
                all_rooms = db.reference('Rooms').get()
                
                if all_rooms:
                    found = False
                    for r_id, r_data in all_rooms.items():
                        players_data = r_data.get('players', {})
                        
                        for t_letter, t_info in players_data.items():
                            # لو لقينا فريق كود الدخول بتاعه بيطابق الـ 3 أرقام اللي اللاعب كتبها
                            if t_info.get('entry_code') == val:
                                t_name = t_info.get('name', "الفريق")
                                
                                # حفظ بيانات الغرفة والفريق المكتشف في الجلسة الحالية
                                session.update({
                                    "room_id": r_id, 
                                    "team_id": t_letter, 
                                    "team_name": t_name
                                })
                                
                                # تحديث الفايربيس إن الفريق ده دخل وجاهز
                                db.reference(f'Rooms/{r_id}/players/{t_letter}').update({
                                    'joined': True,
                                    'status': 'متصل'
                                })
                                
                                found = True
                                show_room_lobby()  # نقله فوراً للوبي اللعبة
                                break
                        if found: break
                    
                    if not found:
                        page.snack_bar = ft.SnackBar(ft.Text("الكود ده غير صحيح أو الغرفة مش موجودة!"))
                        page.snack_bar.open = True
                        page.update()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("لا توجد غرف نشطة حالياً!"))
                    page.snack_bar.open = True
                    page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("يرجى إدخال كود مكون من 3 أرقام فقط (مثال: 412)"))
                page.snack_bar.open = True
                page.update()

        # زر الدخول اللي هيشغل الدالة
        join_btn = ft.FilledButton(
            content=ft.Text("الاتصال بالغرفه", size=18, weight="bold"),
            on_click=on_join,
            width=200,
            height=50,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.RED_800,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=12)
            )
        )

        # إضافة العناصر للشاشة وعرض الخلفية المتحركة علشان متظهرش بيضاء
        page.add(
            ft.Stack([
                ft.Image(src="bg2.gif", fit="cover", width=page.width, height=page.height),
                ft.Container(
                    content=ft.Column([
                        #ft.Text("انضم لغرفة فريقك 🚍", size=26, weight="bold", color="white"),
                        ft.Divider(height=10, color="transparent"),
                        code_in, 
                        ft.Divider(height=5, color="transparent"),
                        join_btn,
                        ft.Divider(height=10, color="transparent"),
                        #ft.TextButton("رجوع للقائمة الرئيسية", on_click=lambda _: show_multiplayer_selection(), style=ft.ButtonStyle(color="white"))
                    ], horizontal_alignment="center", alignment="center"),
                    alignment=ft.Alignment(0, 0), expand=True
                )
            ], expand=True)
        )
        page.update()
                
    show_main_menu()

ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8550)