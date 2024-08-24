from utils import load_infos
import os


def genHTML(booom_type):
    infos = load_infos(booom_type)
    if len(infos) == 0:
        return
    x = [info.date for info in infos]
    with open("./html/" + booom_type + ".html", "w") as html_file:
        html_file.write(
            '<div>\n\t<canvas id="GCoresOriginalGameStars"></canvas>\n</div>\n'
            + '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n'
            + "<script>\n\tconst ctx = document.getElementById('GCoresOriginalGameStars');\n"
            + "\tnew Chart(ctx, {\n"
            + "\t\ttype: 'line',\n"
            + "\t\tdata: {\n"
            + "\t\t\tlabels: %s,\n" % (str(x))
            + "\t\t\tdatasets: ["
        )

        for i in range(len(infos[-1].infos)):
            info = infos[-1].infos[i]
            y = []
            for j in range(len(infos)):
                star = infos[j].find(info.id)
                y.append(star)
            # set thresh
            if booom_type == "all" and max(y) < 30:
                continue
            str_y = str(y).replace("-1", "null")
            if i != 0:
                html_file.write(",\n")
            html_file.write(
                '{\nlabel: "%s",\ndata: %s,\nspanGaps: true,\nfill: false,\ntension: 0.1\n}'
                % (info.title, str_y)
            )

        html_file.write(
            "]\n},\noptions: {\ninteraction: {\nintersect: false\n},\nscales: {\ny: {\nbeginAtZero: true\n}\n}\n}\n});\n</script>"
        )


if __name__ == "__main__":
    booom_types = ["24Porsche"]
    for booom_type in booom_types:
        genHTML(booom_type)
