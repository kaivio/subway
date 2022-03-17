import json
import math

def main():
    data = {}
    with open('data/guang_zhou.json') as f:
        data = json.load(f)

    linemap = {}
    sitemap = {}
    for line in data['l']:
        linemap[line['ls']] = line
        last = None
        for site in line['st']:
            sitemap[site['si']] = site
            x,y = [int(n) for n in site['p'].split()]
            site['p'] = (x,y) 
            site['last'] = last
            site['next'] = None
            if last:
                last['next'] = site
            last = site

      
    lay_line = ''
    lay_site = ''
    lay_text = ''
    
    # 绘制线路
    for _,line in linemap.items():
        color = "#"+line['cl']
        d = ''
        for c in line['c']:
            x,y = c.split()
            if d == '':
                d += f'M{x},{y}'
                continue

            d += f'L{x},{y}'
        
        lay_line += f'<path d="{d}" stroke="{color}" stroke-width="2" fill="none"/>'
        # 线路标签
        for lp in line['lp']:
            x,y = lp.split()
            name = line['ln']
            rtl = ''
            if int(x) >= 2000:
                rtl = True
            lay_line += f'''
            <text x="{x}" y="{y}"
                 stroke-width="0.75em"
                 stroke="{color}"
                {rtl and 'direction="rtl"'}
            >{name}</text>
            <text x="{x}" y="{y}"
                fill="#FFF" 
                {rtl and 'direction="rtl"'}
            >{name}</text>
            '''

    # 绘制站点
    for _, site in sitemap.items():
        x,y = site['p']
        reps = site['r'].split('|')
        circles = []
        r = 4
        for k in reps:
            color = linemap[k]['cl']
            circles.append(f'''<circle 
                cx="{x}" cy="{y}" 
                r="{r}" 
                stroke="#{color}"
                stroke-width="2"
                fill="#fff" 
            />''')
            r += 2

        lay_site += ''.join(reversed(circles))

        name = site['n']
        lg = int(site['lg'])
        ly = y
        if lg in [7,0,1]:
            ly = y-10
        if lg in [6,  2]:
            ly = y + 4
        if lg in [5,4,3]:
            ly = y+10 + 4
    
        lx = x + 10
        dx = 0
        rtl = ''
        if lg in [0,4]:
            dx = f'-{len(name)/2}em'
            lx = x
        if lg in [7,6,5]:
            lx -= 20
            rtl = True

        lay_text += f'''<text
            font-size="10"
            x="{lx}"
            y="{ly}"
            dx="{dx}"
            {rtl and 'direction="rtl"'}
        >{name}</text>
        '''

        
    
    with open('guang_zhou.svg','w') as f:
        f.write(mksvg(
            lay_line+lay_site+lay_text,
            (2000,2000),
            bg="#fff",
            padding=100,
        ))

def hex2rgb(v):
    a = [v[i:i+2] for i in range(0,len(v),2)]
    return tuple([int(n,16) for n in a])


# 返回一个 p1-p2 直角点，该点远离 p0-p2
def find_angle(x0,y0,x1,y1,x2,y2):
    # 判断 p1-p2 是水平或垂直线
    if x1 == x2 or y1 == y2:
        return None, None
    # 判断p1是否在p0-p2之上(向量叉积, v == v2) 
    v =  (x1 - x0) * (y2 - y0)
    v2 = (x2 - x0) * (y1 - y0)

    # 判断p1是否大概在p0-p2之上(点到直线距离) 
    dis = distance(x1,y1,x0,y0,x2,y2)
    print(dis)
    if dis < 20:
        return None, None
        
    ap1 = (x1,y2)
    ap2 = (x2,y1)
    ap = ap1

    return ap


def line_length(x1,y1,x2,y2):
    '''计算线的长度'''
    # 两条直角边的长度
    a = abs(x1 - x2)
    b = abs(y1 - y2)
    # 斜边长度
    c = (a**2 + b**2) ** 0.5
    return c

def distance(px,py,lx1,ly1,lx2,ly2 ):
    '''计算点到直线的距离'''
    # 相切于三角形(p,l1,l2)的矩形
    mx1 = min(px,lx1,ly1)
    my1 = min(py,ly1,ly2)
    mx2 = max(px,lx1,ly1)
    my2 = max(py,ly1,ly2)
    
    # 三角形的面积 (相切矩形的一半)
    area = (mx2-mx1) * (my2-my1) / 2

    # 以线为底边求出高
    h = area * 2 / line_length(lx1,ly1,lx2,ly2)
    return h


    

def mksvg(content,size,bg=None,padding=0, viewBox=None,**attr):
    w,h = size
    bw = w + padding
    bh = h + padding
    x = (bw - w) / 2
    y = (bh - h) / 2

    bg = bg and f'<rect x="0" y="0" width="{bw}" height="{bh}" fill="{bg}"/>' or ''
    viewBox = viewBox or f'0 0 {bw} {bh}'
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{bw}" height="{bh}" viewBox="{viewBox}">
  {bg}
  <svg x="{x}" y="{y}" 
    width="{w}"
    height="{h}"
    style="overflow: visible"
  >
    {content}
  </svg>
</svg>
'''


if __name__ == "__main__":
    main()
