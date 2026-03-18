from manim import *
import numpy as np


# ── Color palette (matching the infographic) ──────────────────────────
DARK_BG = "#0a0e2a"
GOLD = "#e8b825"
LIGHT_GOLD = "#f5d56e"
SOFT_WHITE = "#e0ddd5"
ACCENT_BLUE = "#1a2366"


class BackpropagationAnimation(Scene):
    """Full animation explaining the Backpropagation algorithm,
    based on the Atarraia infographic slides."""

    def setup(self):
        self.camera.background_color = DARK_BG

    # ── helpers ────────────────────────────────────────────────────────
    def atarraia_label(self):
        return (
            Text("A T A R R A I A", font_size=18, color=GOLD)
            .to_corner(UL, buff=0.4)
        )

    def section_label(self, text):
        return (
            Text(text, font_size=18, color=GOLD)
            .to_edge(DOWN, buff=0.35)
        )

    def gold_line(self, y):
        return Line(LEFT * 6, RIGHT * 6, color=GOLD, stroke_width=1.5).shift(UP * y)

    # ── Scene 1 – Title ───────────────────────────────────────────────
    def scene_title(self):
        top_line = self.gold_line(3.2)
        bot_line = self.gold_line(-2.8)

        # Neural network icon (simple graph)
        circle = Circle(radius=0.65, color=GOLD, fill_opacity=1).shift(UP * 1.2)
        dots = VGroup(*[
            Dot(circle.get_center() + 0.4 * np.array([np.cos(a), np.sin(a), 0]),
                color=DARK_BG, radius=0.06)
            for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)
        ])
        edges = VGroup(*[
            Line(d1.get_center(), d2.get_center(), color=DARK_BG, stroke_width=1.2)
            for i, d1 in enumerate(dots) for d2 in dots[i + 1:]
        ])
        icon = VGroup(circle, edges, dots)

        title1 = Text("ALGORITMO", font_size=72, color=GOLD, weight=BOLD).next_to(icon, DOWN, buff=0.5)
        title2 = Text("backpropagation", font_size=52, color=GOLD, slant=ITALIC).next_to(title1, DOWN, buff=0.15)

        brand = Text("A T A R R A I A", font_size=20, color=GOLD).to_edge(DOWN, buff=0.4)

        self.play(
            Create(top_line), Create(bot_line),
            FadeIn(icon, scale=0.8),
            run_time=1,
        )
        self.play(Write(title1), Write(title2), FadeIn(brand), run_time=1.5)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 2 – The problem with gradient descent ───────────────────
    def scene_problem(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        title = Text("EL PROBLEMA DEL", font_size=44, color=SOFT_WHITE, weight=BOLD).shift(UP * 3)
        subtitle = Text("descenso del gradiente", font_size=36, color=GOLD, slant=ITALIC).next_to(title, DOWN, buff=0.15)

        explanation = Text(
            "Cuando queremos entrenar una red neuronal,\n"
            "el algoritmo más popular para optimizar la\n"
            "función de costo es el descenso del gradiente.",
            font_size=24, color=SOFT_WHITE, line_spacing=1.4,
        ).shift(UP * 0.8)

        cost_text = Text("Este algoritmo es muy costoso:", font_size=24, color=SOFT_WHITE).shift(DOWN * 0.5)

        big_o = MathTex(r"\mathcal{O}(w^2)", font_size=64, color=GOLD).shift(DOWN * 1.5)
        big_o_label = Text(
            "Para cada actualización, calculamos\nla derivada parcial del costo con\nrespecto a cada peso de la red.",
            font_size=20, color=SOFT_WHITE, line_spacing=1.3,
        ).next_to(big_o, DOWN, buff=0.4)

        self.play(FadeIn(header), FadeIn(footer), Write(title), Write(subtitle), run_time=1)
        self.play(FadeIn(explanation, shift=UP * 0.3), run_time=1)
        self.play(FadeIn(cost_text), run_time=0.6)
        self.play(Write(big_o), FadeIn(big_o_label, shift=UP * 0.2), run_time=1.2)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 3 – Backpropagation to the rescue ──────────────────────
    def scene_solution(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        line1 = Text(
            "Podemos utilizar un nuevo algoritmo\nque reduce el costo a",
            font_size=26, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(UP * 2.5)
        ow = MathTex(r"\mathcal{O}(w)", font_size=56, color=GOLD).next_to(line1, DOWN, buff=0.3)

        big_title = Text("backpropagation", font_size=56, color=GOLD, slant=ITALIC).shift(UP * 0.2)

        chain_text = Text(
            "Este algoritmo se beneficia de la red\ncomo composición de funciones\npara aplicar la regla de la cadena:",
            font_size=24, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(DOWN * 1)

        chain_rule = MathTex(
            r"\frac{d}{dx}\,g(h(x)) = g'(h(x)) \cdot h'(x)",
            font_size=44, color=GOLD,
        ).shift(DOWN * 2.5)

        self.play(FadeIn(header), FadeIn(footer), run_time=0.5)
        self.play(Write(line1), run_time=0.8)
        self.play(Write(ow), run_time=0.6)
        self.play(FadeIn(big_title, scale=1.2), run_time=1)
        self.play(FadeIn(chain_text, shift=UP * 0.2), run_time=0.8)
        self.play(Write(chain_rule), run_time=1.2)

        # Highlight the chain rule
        box = SurroundingRectangle(chain_rule, color=GOLD, buff=0.2)
        self.play(Create(box), run_time=0.6)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 4 – Example neural network ─────────────────────────────
    def scene_example(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        ex_title = Text("Un ejemplo:", font_size=36, color=GOLD, weight=BOLD, slant=ITALIC).to_edge(UP, buff=0.8).shift(LEFT * 3)
        desc = Text("Imaginemos una red neuronal sencilla", font_size=28, color=SOFT_WHITE).next_to(ex_title, DOWN, buff=0.25, aligned_edge=LEFT)

        f_def = MathTex(r"f : \mathbb{R} \to \mathbb{R}", font_size=44, color=GOLD).shift(UP * 1.5)
        f_eq = MathTex(
            r"f(x) = \sigma(w_2 \,\sigma(w_1 x + b_1) + b_2)",
            font_size=38, color=GOLD,
        ).next_to(f_def, DOWN, buff=0.3)

        # Simple network diagram
        positions = [LEFT * 3, ORIGIN, RIGHT * 3]
        labels_txt = ["x", "z_1", "z_2"]
        nodes = VGroup()
        node_labels = VGroup()
        for pos, ltxt in zip(positions, labels_txt):
            dot = Dot(pos + DOWN * 1.3, radius=0.12, color=GOLD)
            lab = MathTex(ltxt, font_size=30, color=SOFT_WHITE).next_to(dot, DOWN, buff=0.25)
            nodes.add(dot)
            node_labels.add(lab)

        # bias nodes
        bias_nodes = VGroup()
        for pos in positions[:2]:
            bd = Dot(pos + DOWN * 1.3 + DOWN * 0.7, radius=0.08, color=GOLD)
            bias_nodes.add(bd)

        # edges
        w_labels = [r"w_1", r"w_2"]
        b_labels = [r"b_1", r"b_2"]
        edge_group = VGroup()
        w_label_group = VGroup()
        b_label_group = VGroup()
        for i in range(2):
            e = Line(nodes[i].get_center(), nodes[i + 1].get_center(), color=GOLD, stroke_width=2)
            wl = MathTex(w_labels[i], font_size=24, color=GOLD).next_to(e, UP, buff=0.1)
            be = DashedLine(bias_nodes[i].get_center(), nodes[i + 1].get_center(), color=GOLD, stroke_width=1.5)
            bl = MathTex(b_labels[i], font_size=24, color=GOLD).next_to(be, DOWN, buff=0.05)
            edge_group.add(e, be)
            w_label_group.add(wl)
            b_label_group.add(bl)

        network = VGroup(edge_group, nodes, bias_nodes, node_labels, w_label_group, b_label_group).shift(DOWN * 0.2)

        # Cost function
        cost_title = Text("Donde la función de costo es", font_size=26, color=SOFT_WHITE).shift(DOWN * 2.3)
        cost_eq = MathTex(
            r"L = \frac{1}{2}(y - \hat{y})^2",
            font_size=40, color=GOLD,
        ).shift(DOWN * 3)

        self.play(FadeIn(header), FadeIn(footer), Write(ex_title), FadeIn(desc), run_time=1)
        self.play(Write(f_def), Write(f_eq), run_time=1.2)
        self.play(
            *[GrowFromCenter(n) for n in nodes],
            *[GrowFromCenter(n) for n in bias_nodes],
            *[Create(e) for e in edge_group],
            *[FadeIn(l) for l in node_labels],
            *[FadeIn(l) for l in w_label_group],
            *[FadeIn(l) for l in b_label_group],
            run_time=1.5,
        )
        self.play(FadeIn(cost_title), Write(cost_eq), run_time=1)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 5 – Gradient computation ────────────────────────────────
    def scene_gradient(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        intro = Text(
            "Para realizar descenso del gradiente\ntendríamos que calcular:",
            font_size=26, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(UP * 2.8)

        grad = MathTex(
            r"\nabla L = \left("
            r"\frac{\partial L}{\partial w_1},\;"
            r"\frac{\partial L}{\partial b_1},\;"
            r"\frac{\partial L}{\partial w_2},\;"
            r"\frac{\partial L}{\partial b_2}"
            r"\right)",
            font_size=36, color=GOLD,
        ).shift(UP * 1.3)

        chain_intro = Text(
            "Analizando las derivadas por regla de la cadena:",
            font_size=24, color=SOFT_WHITE,
        ).shift(UP * 0.3)

        # Last layer derivatives
        dw2 = MathTex(
            r"\frac{\partial L}{\partial w_2} = (\hat{y}-y)\,\sigma'(a_2)\,z_1",
            font_size=32, color=GOLD,
        ).shift(DOWN * 0.6)
        db2 = MathTex(
            r"\frac{\partial L}{\partial b_2} = (\hat{y}-y)\,\sigma'(a_2)",
            font_size=32, color=GOLD,
        ).next_to(dw2, DOWN, buff=0.35)

        # Previous layer derivatives
        dw1 = MathTex(
            r"\frac{\partial L}{\partial w_1} = (\hat{y}-y)\,\sigma'(a_2)\,w_2\,\sigma'(a_1)\,x",
            font_size=32, color=GOLD,
        ).next_to(db2, DOWN, buff=0.55)
        db1 = MathTex(
            r"\frac{\partial L}{\partial b_1} = (\hat{y}-y)\,\sigma'(a_2)\,w_2\,\sigma'(a_1)",
            font_size=32, color=GOLD,
        ).next_to(dw1, DOWN, buff=0.35)

        self.play(FadeIn(header), FadeIn(footer), Write(intro), run_time=0.8)
        self.play(Write(grad), run_time=1.2)
        self.play(FadeIn(chain_intro), run_time=0.6)
        self.play(Write(dw2), run_time=0.8)
        self.play(Write(db2), run_time=0.8)
        self.play(Write(dw1), run_time=0.8)
        self.play(Write(db1), run_time=0.8)
        self.wait(1)

        # Highlight repeated parts
        # The common factor (y_hat - y) sigma'(a2) in last layer
        box_last = SurroundingRectangle(
            VGroup(dw2, db2), color=LIGHT_GOLD, buff=0.15
        )
        note_last = Text("¡Este trozo se repite\ndesde la última capa!", font_size=20, color=LIGHT_GOLD).next_to(box_last, RIGHT, buff=0.3)

        box_prev = SurroundingRectangle(
            VGroup(dw1, db1), color=LIGHT_GOLD, buff=0.15
        )
        note_prev = Text("¡Este trozo se repite\nen la penúltima capa!", font_size=20, color=LIGHT_GOLD).next_to(box_prev, RIGHT, buff=0.3)

        self.play(Create(box_last), FadeIn(note_last), run_time=0.8)
        self.wait(1)
        self.play(Create(box_prev), FadeIn(note_prev), run_time=0.8)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 6 – The magic: patterns ─────────────────────────────────
    def scene_magic(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        magic = Text(
            "¡Ahí está la magia!",
            font_size=40, color=SOFT_WHITE, weight=BOLD,
        ).shift(UP * 3)
        sub = Text(
            "Hay patrones en las derivadas.\nHay información que se repite.",
            font_size=26, color=SOFT_WHITE, line_spacing=1.3,
        ).next_to(magic, DOWN, buff=0.3)

        explanation = Text(
            "Si calculo las derivadas de las últimas capas,\n"
            "hay información de este cálculo que se repite\n"
            "en sus capas previas.",
            font_size=24, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(UP * 0.5)

        # Show the two layers again with arrows between them
        last_label = Text("Última capa", font_size=22, color=GOLD, slant=ITALIC).shift(DOWN * 0.5 + LEFT * 4.5)
        dw2 = MathTex(
            r"\frac{\partial L}{\partial w_2} = (\hat{y}-y)\,\sigma'(a_2)\,z_1",
            font_size=28, color=GOLD,
        ).shift(DOWN * 0.8)
        db2 = MathTex(
            r"\frac{\partial L}{\partial b_2} = (\hat{y}-y)\,\sigma'(a_2)",
            font_size=28, color=GOLD,
        ).next_to(dw2, DOWN, buff=0.25)

        arrows = VGroup(*[
            Arrow(UP * 0.15, DOWN * 0.5, color=GOLD, stroke_width=3).shift(DOWN * 1.8 + RIGHT * x)
            for x in [-1, 0, 1]
        ])

        prev_label = Text("Capa previa", font_size=22, color=GOLD, slant=ITALIC).shift(DOWN * 2.5 + LEFT * 4.5)
        dw1 = MathTex(
            r"\frac{\partial L}{\partial w_1} = (\hat{y}-y)\,\sigma'(a_2)\,w_2\,\sigma'(a_1)\,x",
            font_size=28, color=GOLD,
        ).shift(DOWN * 2.8)
        db1 = MathTex(
            r"\frac{\partial L}{\partial b_1} = (\hat{y}-y)\,\sigma'(a_2)\,w_2\,\sigma'(a_1)",
            font_size=28, color=GOLD,
        ).next_to(dw1, DOWN, buff=0.25)

        self.play(FadeIn(header), FadeIn(footer), run_time=0.4)
        self.play(Write(magic), run_time=0.8)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(explanation, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(last_label), Write(dw2), Write(db2), run_time=1)
        self.play(*[GrowArrow(a) for a in arrows], run_time=0.8)
        self.play(FadeIn(prev_label), Write(dw1), Write(db1), run_time=1)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 7 – Backpropagation in action ───────────────────────────
    def scene_backprop_action(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        text1 = Text(
            "Si entonces calculamos las derivadas,\n"
            "de atrás para adelante, en términos de\n"
            "capas, podremos reutilizar cálculos.",
            font_size=26, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(UP * 2.5)

        # Network diagram with backward arrow
        positions = [LEFT * 3, ORIGIN, RIGHT * 3]
        labels_txt = ["x", "z_1", "z_2"]
        nodes = VGroup()
        node_labels = VGroup()
        for pos, ltxt in zip(positions, labels_txt):
            dot = Dot(pos + DOWN * 0.5, radius=0.12, color=GOLD)
            lab = MathTex(ltxt, font_size=30, color=SOFT_WHITE).next_to(dot, DOWN, buff=0.25)
            nodes.add(dot)
            node_labels.add(lab)

        edges = VGroup()
        for i in range(2):
            e = Line(nodes[i].get_center(), nodes[i + 1].get_center(), color=GOLD, stroke_width=2)
            edges.add(e)

        # Derivative labels above each layer pair
        d_right = MathTex(
            r"\frac{\partial L}{\partial w_2},\;\frac{\partial L}{\partial b_2}",
            font_size=24, color=GOLD,
        ).next_to(nodes[2], UP, buff=0.6)
        d_left = MathTex(
            r"\frac{\partial L}{\partial w_1},\;\frac{\partial L}{\partial b_1}",
            font_size=24, color=GOLD,
        ).next_to(nodes[0], UP, buff=0.6)

        back_arrow = Arrow(
            d_right.get_left() + LEFT * 0.2,
            d_left.get_right() + RIGHT * 0.2,
            color=GOLD, stroke_width=4,
        )

        network = VGroup(edges, nodes, node_labels).shift(DOWN * 0.2)

        # Final message
        final_text = Text(
            "Se dice que el error se propaga de atrás\n"
            "hacia adelante, y de ahí nace el nombre\n"
            "del algoritmo: backpropagation.",
            font_size=24, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(DOWN * 2.5)

        self.play(FadeIn(header), FadeIn(footer), run_time=0.4)
        self.play(Write(text1), run_time=1)
        self.play(
            *[GrowFromCenter(n) for n in nodes],
            *[Create(e) for e in edges],
            *[FadeIn(l) for l in node_labels],
            run_time=1,
        )
        self.play(FadeIn(d_right), run_time=0.6)
        self.play(GrowArrow(back_arrow), run_time=1)
        self.play(FadeIn(d_left), run_time=0.6)
        self.play(FadeIn(final_text, shift=UP * 0.3), run_time=1)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ── Scene 8 – Closing ────────────────────────────────────────────
    def scene_closing(self):
        header = self.atarraia_label()
        footer = self.section_label("BACKPROPAGATION")

        text = Text(
            "Pero aún hay más detalles que se\npueden comprender en este tema.",
            font_size=28, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(UP * 2)

        cta = Text(
            "Puedes visitar el canal de YouTube del\nSemillero AtarraiA de Redes Neuronales",
            font_size=26, color=SOFT_WHITE, weight=BOLD, line_spacing=1.3,
        ).shift(UP * 0.3)

        cta2 = Text(
            "También puedes participar en\nfuturas reuniones uniéndote al\nlink del meet en la descripción.",
            font_size=24, color=SOFT_WHITE, line_spacing=1.3,
        ).shift(DOWN * 1.5)

        # Atarraia big brand
        brand = Text("ATARRAIA", font_size=72, color=GOLD, weight=BOLD).shift(DOWN * 3)

        self.play(FadeIn(header), FadeIn(footer), run_time=0.4)
        self.play(Write(text), run_time=1)
        self.play(FadeIn(cta, shift=UP * 0.2), run_time=1)
        self.play(FadeIn(cta2, shift=UP * 0.2), run_time=1)
        self.play(FadeIn(brand, scale=0.8), run_time=1)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)

    # ── Construct ─────────────────────────────────────────────────────
    def construct(self):
        self.scene_title()
        self.scene_problem()
        self.scene_solution()
        self.scene_example()
        self.scene_gradient()
        self.scene_magic()
        self.scene_backprop_action()
        self.scene_closing()
