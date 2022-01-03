#!/usr/bin/env python3
import PySimpleGUI as sg
import re

class BaseConverter():
    def __init__(self):
        self.dec_value = 0

        # 正規表現 (Regular expression)：[+][-] button KEY
        self.sign_btn_pattern = re.compile(r'dec-(?P<SIGN>plus|minus)')

        # 正規表現 (Regular expression)：numeric button KEY
        self.value_btn_pattern = re.compile(r'^(btn|inp)-(?P<BASE>bin|oct|hex|dec)-(?P<POS>\d+)')

        bit_frame_list = []
        bit_frame_list.append(sg.Frame("BIT", [
                        [sg.Text("BIN:")],
                        [sg.Text("OCT:")],
                        [sg.Text("HEX:")]], title_location=sg.TITLE_LOCATION_TOP))

        # 数値 button を作成
        oct_idx = 5     # OCT 6桁 = 5 4 3 2 1 0
        hex_idx = 3     # HEX 4桁 = 3 2 1 0
        for bit in reversed(range(16)):
            # BIN button : 1 bit
            btn_bit = sg.Button('0', size=(1,1), key="btn-bin-{:d}".format(bit), enable_events=True, button_color=('#000000','#ffffff'))

            if (bit % 3) == 0:
                # OCT button : 3 bits 毎に作成
                btn_oct = sg.Button('0', size=(1,1), key="btn-oct-{:d}".format(oct_idx), button_color=('#000000','#ffffff'))
                oct_idx = oct_idx - 1
            else:
                # OCT button が不要なビット位置にも無効 button を作成（無いとFrame()内の button 位置がビット毎にずれる）
                btn_oct = sg.Button(' ', size=(1,1), key="oct{:d}".format(bit), disabled=True, button_color="#64778d")

            if (bit % 4) == 0:
                # HEX button : 4 bits 毎に作成
                btn_hex = sg.Button('0', size=(1,1), key="btn-hex-{:d}".format(hex_idx), button_color=('#000000','#ffffff'))
                hex_idx = hex_idx - 1
            else:
                # HEX button が不要なビット位置にも無効 button を作成（無いとフレーム()内の button 位置がビット毎にずれる）
                btn_hex = sg.Button(' ', size=(1,1), key="hex{:d}".format(bit), disabled=True, button_color="#64778d")

            # Frame(1bit : BIN, OCT, HEX) を作成
            bit_frame_list.append(sg.Frame("{:>2d}".format(bit), [[btn_bit], [btn_oct], [btn_hex]],
                title_location=sg.TITLE_LOCATION_TOP, element_justification='center'))

        # DEC: テキストフィールドの変更イベントが必要なので Spin ではなく Input を使用
        #      Spin → (Input, [+], [-])  (need to fire the text field change event)
        self.layout = [[sg.Text("DEC:"), sg.Input('', size=(7, 1), key="inp-dec-0", enable_events=True),
                        sg.Button('+', key="dec-plus"), sg.Button('-', key="dec-minus")],
                       [sg.Text("BIN:"), sg.Text('', key="disp-bin")],
                       [sg.Text("OCT:"), sg.Text('', key="disp-oct")],
                       [sg.Text("HEX:"), sg.Text('', key="disp-hex")],
                       bit_frame_list,
                       [sg.Button('Exit')] ]

        self.window = sg.Window('BaseConverter', self.layout)

    # BIN: Text と button を更新
    def update_bin(self):
        # BIN Text 更新
        self.window['disp-bin'].Update("{:>b}".format(self.dec_value))

        # BIN の各 button 更新
        mask = 0x0001
        for bit in range(16):
            key = "btn-bin-{:d}".format(bit)

            if (self.dec_value & mask) == 0:
                bit_str = "0"
            else:
                bit_str = "1"

            if self.window[key].ButtonText != bit_str:
                self.window[key].Update(bit_str)

            mask = mask << 1

    # OCT: Text と button を更新
    def update_oct(self):
        # OCT Text 更新
        self.window['disp-oct'].Update("{:>o}".format(self.dec_value))

        # OCT を6桁にして逆順（1文字ずつ）にする
        # octstr[0] = 8**0 (0乗)、octstr[1] = 8**1 (1乗) ・・・、octstr[5] = 8**5 (5乗)
        octstr = list(('{:06o}'.format(self.dec_value))[::-1])

        # OCT の button を更新
        for idx in range(6):
            key = "btn-oct-{:d}".format(idx)
            if self.window[key].ButtonText != octstr[idx]:
                self.window[key].Update(octstr[idx])

    # HEX: Text と button を更新
    def update_hex(self):
        # HEX Text 更新
        self.window['disp-hex'].Update("{:>X}".format(self.dec_value))

        # HEX を4桁にして逆順（1文字ずつ）にする
        # hexstr[0] = 16**0 (0乗)、hexstr[1] = 16**1 (1乗) ・・・、hexstr[5] = 16**5 (5乗)
        hexstr = list(('{:04X}'.format(self.dec_value))[::-1])

        # HEX の button を更新
        for idx in reversed(range(4)):
            key = "btn-hex-{:d}".format(idx)
            if self.window[key].ButtonText != hexstr[idx]:
                self.window[key].Update(hexstr[idx])

    # DEC Input
    def update_dec(self):
        key = "inp-dec-0"
        self.window[key].Update("{:d}".format(self.dec_value))

    def onclik_bin(self, pos):
        # BIN button （0 → 1）（1 → 0）
        key = "btn-bin-{:d}".format(pos)
        if self.window[key].ButtonText == '0':
            self.window[key].Update("1")
        else:
            self.window[key].Update("0")

        # BIN buttons → number (ボタンの0/1 を並べて BIN 文字列を作成)
        num_str = ""
        for bit in reversed(range(16)):
            key = "btn-bin-{:d}".format(bit)
            num_str = num_str + self.window[key].ButtonText

        self.dec_value = int(num_str, 2)

        self.window['disp-bin'].Update("{:>b}".format(self.dec_value))

        self.update_oct()
        self.update_dec()
        self.update_hex()

    def onclik_oct(self, pos):
        # OCT button 更新（0 → 1）（1 → 2）・・・（7 → 0）
        key = "btn-oct-{:d}".format(pos)
        val = (int(self.window[key].ButtonText, 8) + 1) & 7
        if (pos == 5):
            # 全体で16ビットにしているため、8の5乗の位は2以上にならないようにする
            val = val & 1
        self.window[key].Update("{:o}".format(val))

        # OCT buttons → number (ボタンの0～7 を並べて OCT 文字列を作成)
        num_str = ""
        for idx in reversed(range(6)):
            key = "btn-oct-{:d}".format(idx)
            num_str = num_str + self.window[key].ButtonText
        self.dec_value = int(num_str, 8)

        self.window['disp-oct'].Update("{:>o}".format(self.dec_value))

        self.update_bin()
        self.update_dec()
        self.update_hex()

    def onclik_hex(self, pos):
        # HEX button 更新（0 → 1）（1 → 2）・・・（F → 0）
        key = "btn-hex-{:d}".format(pos)
        val = (int(self.window[key].ButtonText, 16) + 1) & 0x0F
        self.window[key].Update("{:X}".format(val))

        # HEX buttons → number (ボタンの0～F を並べて HEX 文字列を作成)
        num_str = ""
        for idx in reversed(range(4)):
            key = "btn-hex-{:d}".format(idx)
            num_str = num_str + self.window[key].ButtonText
        self.dec_value = int(num_str, 16)

        self.window['disp-hex'].Update("{:>X}".format(self.dec_value))

        self.update_bin()
        self.update_oct()
        self.update_dec()

    # DEC が変更されたときの処理
    def onchange_dec(self, dec_num_str):
        try:
            d_val = int(dec_num_str)
            if (d_val > 0xFFFF):
                d_val = 0xFFFF
        except:
            if dec_num_str == "":
                d_val = 0
            else:
                d_val = self.dec_value

        # DEC 表示
        if (dec_num_str != str(d_val)):
            self.window["inp-dec-0"].Update(str(d_val))

        if self.dec_value != d_val:
            self.dec_value = d_val
            self.update_bin()
            self.update_oct()
            self.update_hex()

    # DEC [+] or [-]
    def onchange_plus_minus(self, dec_num_str, sign):
        try:
            d_val = int(dec_num_str)
            if sign == 'plus':
                # [+] button = 10進数を + 1
                d_val = d_val + 1
                if (d_val > 0xFFFF):
                    d_val = 0xFFFF
            else:
                # [-] button = 10進数を - 1
                d_val = d_val - 1
                if (d_val < 0):
                    d_val = 0
        except:
            d_val = self.dec_value

        # DEC 表示
        if (dec_num_str != str(d_val)):
            self.window["inp-dec-0"].Update(str(d_val))

        if self.dec_value != d_val:
            self.dec_value = d_val
            self.update_bin()
            self.update_oct()
            self.update_hex()

    def main_loop(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            # [+][-] button ?
            m = self.sign_btn_pattern.match(event)
            if m:
                self.onchange_plus_minus(values["inp-dec-0"], m.group('SIGN'))
                continue

            # numeric button ?
            m = self.value_btn_pattern.match(event)
            if m:
                base_type = m.group('BASE')     # 基底
                pos = int(m.group('POS'))       # button 位置

                if base_type == 'dec':
                    self.onchange_dec(values[event])

                elif base_type == 'bin':
                    self.onclik_bin(pos)

                elif base_type == 'oct':
                    self.onclik_oct(pos)

                elif base_type == 'hex':
                    self.onclik_hex(pos)

        self.window.close()

if __name__ == '__main__':
    bc = BaseConverter()
    bc.main_loop()

