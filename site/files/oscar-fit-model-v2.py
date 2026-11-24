import sys, json
import cadquery as cq
src, outdir = sys.argv[1], sys.argv[2]
s = cq.importers.importStep(src)
solids = []
for v in s.vals(): solids += v.Solids()
def bbt(so):
    b = so.BoundingBox(); return (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)
B = [bbt(so) for so in solids]

# Cavity measured by probes: X left-right, Y up, Z back(-288) to front(-170.8)
CAV = (-167.9,-38.4, 55.7,181.7, -288.0,-170.8)
# name: (x0,x1,y0,y1,z0,z1, kind, colour, note)
C = {
 "pi5_with_cooler":      (-166,-141,  66,122, -286,-201, "part", (0.1,0.6,0.2), "Pi 5 85x56 board, 25 thick incl. cooler and standoffs, on edge against left wall"),
 "pi5_usb_plugs":        (-166,-141,  66,122, -201,-178, "clearance", (0.6,0.9,0.6), "USB plugs: Arduino cable, microphone"),
 "pi5_power_camera":     (-166,-141, 122,137, -286,-201, "clearance", (0.6,0.9,0.6), "USB-C power plug and camera ribbon on the upper long edge"),
 "battery_gba12v_3ah":   ( -96, -44,  65,117, -268,-168, "part", (0.85,0.1,0.1), "Bosch GBA 12V 3.0Ah 47x50x86 plus 2.5 mm holder walls and 14 mm dock at the rear"),
 "arduino_motor_shield": ( -98, -44, 120,149, -286,-217, "part", (0.1,0.3,0.8), "Uno 68.6x53.4 with Motor Shield Rev3, 29 high"),
 "arduino_usb_plug":     ( -98, -44, 120,149, -217,-190, "clearance", (0.6,0.7,0.95), "USB-B plug"),
 "ai_hat_reserve":       (-141,-126,  66,122, -286,-201, "reserve", (0.2,0.8,0.8), "Reserved, empty: 15 mm for a HAT stacked on the Pi (16 mm header). Pi PCIe connector stays free"),
 "buck_converter_5v":    (-124,-104,  65,100, -286,-221, "part", (0.9,0.6,0.1), "ASSUMED 65x35x20, real size unknown. On edge"),
 "pca9685_servo_driver": (-124,-102, 104,130, -286,-223, "part", (0.5,0.2,0.7), "Adafruit 815, 62.5x25.4, 22 thick with servo plugs. On edge"),
 "speaker":              (-139, -99, 100,140, -192,-172, "part", (0.3,0.3,0.3), "ASSUMED 40 mm diameter, 20 deep, facing the door"),
 "amp_fuse_cutoff":      (-124,-100,  65, 90, -215,-175, "part", (0.8,0.8,0.2), "MAX98357, fuse holder, low-voltage cutoff: allowance 24x25x40"),
}
def box(c):
    x0,x1,y0,y1,z0,z1 = c[:6]
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)).val()
def ov(a,b,m=0.0):
    return a[0]<b[1]-m and a[1]>b[0]+m and a[2]<b[3]-m and a[3]>b[2]+m and a[4]<b[5]-m and a[5]>b[4]+m
res = {"cavity_mm": {"width_x": round(CAV[1]-CAV[0],1), "height_y_to_body_top": round(CAV[3]-CAV[2],1), "height_y_below_servos": round(150.4-CAV[2],1), "depth_z": round(CAV[5]-CAV[4],1)}, "components": {}, "pairs": []}
names = list(C)
ok = True
for n in names:
    c = C[n]; b = box(c)
    inside = c[0]>=CAV[0] and c[1]<=CAV[1] and c[2]>=CAV[2] and c[3]<=CAV[3] and c[4]>=CAV[4] and c[5]<=CAV[5]
    hits = []
    for i,so in enumerate(solids):
        if ov(B[i], c[:6]):
            try:
                v = b.intersect(so).Volume()
            except Exception as e:
                v = -1
            if abs(v) > 1e-3: hits.append((i, round(v,1)))
    # clearances to cavity walls
    cl = {"left": round(c[0]-CAV[0],1), "right": round(CAV[1]-c[1],1), "floor": round(c[2]-CAV[2],1), "to_servo_zone_y150": round(150.4-c[3],1), "back": round(c[4]-CAV[4],1), "front": round(CAV[5]-c[5],1)}
    res["components"][n] = {"size_xyz": [c[1]-c[0], c[3]-c[2], c[5]-c[4]], "kind": c[6], "inside_cavity": inside, "collides_with_assembly_solids": hits, "clearance_mm": cl, "note": c[8]}
    if not inside or hits: ok = False
for i in range(len(names)):
    for j in range(i+1,len(names)):
        a,b = C[names[i]], C[names[j]]
        if ov(a[:6], b[:6]):
            res["pairs"].append((names[i], names[j])); ok = False
res["all_clear"] = ok
vol_cav = (CAV[1]-CAV[0])*(150.4-CAV[2])*(CAV[5]-CAV[4])/1000
vol_c = sum((c[1]-c[0])*(c[3]-c[2])*(c[5]-c[4]) for c in C.values())/1000
res["fill"] = {"free_block_cm3": round(vol_cav), "components_and_clearances_cm3": round(vol_c), "percent": round(100*vol_c/vol_cav)}
json.dump(res, open(outdir+"/fit_result.json","w"), indent=1)
print(json.dumps(res, indent=1))
# export: robot + components
assy = cq.Assembly(name="oscar_fit_model")
assy.add(s.val(), name="wall_e_assembly", color=cq.Color(0.85,0.75,0.3,0.35))
for n in names:
    c = C[n]
    assy.add(box(c), name=n, color=cq.Color(*c[7], 0.6 if c[6]!="part" else 1.0))
pass  # full assembly export skipped (100 MB)
# components only (small file)
comp = cq.Assembly(name="oscar_components")
for n in names:
    c = C[n]; comp.add(box(c), name=n, color=cq.Color(*c[7]))
comp.save(outdir+"/oscar-components-v2.step")
json.dump({n: list(C[n][:6])+[C[n][6], list(C[n][7])] for n in names}, open(outdir+"/components.json","w"))
print("saved")
