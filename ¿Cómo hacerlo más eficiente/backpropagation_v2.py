from manim import *
import numpy as np

# ── Palette ────────────────────────────────────────────────────────────────
BG       = "#07091c"
GOLD     = "#e8b825"
LGOLD    = "#f5d56e"
WHITE    = "#e8e4da"
BLUE     = "#3a7bd5"
LBLUE    = "#7eb8f7"
RED      = "#e84545"
GREEN    = "#2ecc71"
PURPLE   = "#9b59b6"
TEAL     = "#1abc9c"
DARK     = "#0a0e2a"


# ── Helpers ─────────────────────────────────────────────────────────────────
def neuron(pos, r=0.28, fill=DARK, stroke=GOLD, opacity=1.0):
    return Circle(radius=r, color=stroke, fill_color=fill,
                  fill_opacity=opacity, stroke_width=2.5).move_to(pos)

def brand(corner=UL):
    return Text("A T A R R A I A", font_size=16, color=GOLD).to_corner(corner, buff=0.35)


# ── Main scene ──────────────────────────────────────────────────────────────
class BackpropagationV2(Scene):
    """Visually-driven Backpropagation animation — minimal text."""

    def setup(self):
        self.camera.background_color = BG

    # ── Build a reusable network VGroup ─────────────────────────────────
    def make_network(self, layer_sizes, center=ORIGIN, h_gap=2.0, v_gap=0.85, r=0.24):
        """Return (layers_list, edges_list, all_neurons VGroup, all_edges VGroup)."""
        layers = []
        max_n = max(layer_sizes)
        for col, n in enumerate(layer_sizes):
            layer = []
            x = (col - (len(layer_sizes) - 1) / 2) * h_gap
            for row in range(n):
                y = (row - (n - 1) / 2) * v_gap
                c = neuron(np.array([x, y, 0]) + center, r=r)
                layer.append(c)
            layers.append(layer)

        edges = []
        for i in range(len(layers) - 1):
            for n1 in layers[i]:
                for n2 in layers[i + 1]:
                    e = Line(n1.get_center(), n2.get_center(),
                             color=GOLD, stroke_width=0.8, stroke_opacity=0.35)
                    edges.append(e)

        all_n = VGroup(*[c for layer in layers for c in layer])
        all_e = VGroup(*edges)
        return layers, edges, all_n, all_e

    # ══════════════════════════════════════════════════════════════════════
    # Scene 1 — TITLE: network materialises from noise
    # ══════════════════════════════════════════════════════════════════════
    def scene_title(self):
        np.random.seed(42)
        # Scatter of random dots → organized network
        layers, edges, all_n, all_e = self.make_network(
            [3, 5, 5, 3], center=UP * 0.6, h_gap=2.2, v_gap=0.75
        )
        # Start positions: random scatter
        scatter = [
            all_n[i].copy().move_to(np.array([
                np.random.uniform(-5, 5), np.random.uniform(-3, 3), 0
            ]))
            for i in range(len(all_n))
        ]

        title = Text("backpropagation", font_size=60, color=GOLD,
                     slant=ITALIC, weight=BOLD).to_edge(DOWN, buff=0.8)
        sub   = Text("¿Cómo funciona?", font_size=26, color=WHITE).next_to(title, UP, buff=0.2)
        b     = brand()

        # Show scatter first
        scatter_g = VGroup(*scatter)
        self.play(FadeIn(scatter_g, lag_ratio=0.04), run_time=1.2)
        # Move each dot to its network position
        self.play(
            *[s.animate.move_to(t.get_center()) for s, t in zip(scatter, all_n)],
            run_time=1.6, rate_func=smooth,
        )
        # Replace scatter with proper styled neurons
        self.remove(scatter_g)
        self.add(all_e, all_n)
        self.play(
            Create(all_e, lag_ratio=0.02),
            FadeIn(b),
            run_time=1.0,
        )
        self.play(Write(title), FadeIn(sub), run_time=1.2)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 2 — FORWARD PASS: signal pulses layer by layer
    # ══════════════════════════════════════════════════════════════════════
    def scene_forward(self):
        b = brand()
        label = Text("Forward pass", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        layers, edges, all_n, all_e = self.make_network(
            [3, 4, 4, 2], center=UP * 0.2, h_gap=2.2, v_gap=0.8
        )

        x_label = MathTex("x", font_size=36, color=LBLUE).next_to(layers[0][1], LEFT, buff=0.4)
        y_label = MathTex(r"\hat{y}", font_size=36, color=TEAL).next_to(layers[-1][0], RIGHT, buff=0.4)

        self.play(FadeIn(b), FadeIn(label), Create(all_e), FadeIn(all_n),
                  FadeIn(x_label), run_time=1.2)

        # Animate signal through layers
        for li, layer in enumerate(layers):
            # Flash neurons in this layer
            anims = [n.animate.set_fill(LBLUE, opacity=0.85).set_stroke(LBLUE, width=4)
                     for n in layer]
            self.play(*anims, run_time=0.4)
            if li < len(layers) - 1:
                # Show edge pulses to next layer
                next_edges = [
                    e for e in edges
                    if any(np.allclose(e.get_start(), n.get_center(), atol=0.05) for n in layer)
                ]
                self.play(
                    *[e.animate.set_stroke(LBLUE, width=2.5, opacity=1) for e in next_edges],
                    run_time=0.3,
                )
            # Dim back
            self.play(
                *[n.animate.set_fill(DARK, opacity=1).set_stroke(GOLD, width=2.5) for n in layer],
                *([e.animate.set_stroke(GOLD, width=0.8, opacity=0.35) for e in (edges if li < len(layers) - 1 else [])]),
                run_time=0.3,
            )

        self.play(FadeIn(y_label), run_time=0.5)
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 3 — LOSS: output vs target, red error delta
    # ══════════════════════════════════════════════════════════════════════
    def scene_loss(self):
        b     = brand()
        label = Text("Función de costo", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        # Single output neuron
        out_pos  = LEFT * 2 + UP * 0.5
        tgt_pos  = RIGHT * 2 + UP * 0.5
        out_node = neuron(out_pos, r=0.4, stroke=LBLUE)
        tgt_node = neuron(tgt_pos, r=0.4, stroke=GREEN)

        y_hat = MathTex(r"\hat{y}", font_size=38, color=LBLUE).move_to(out_node)
        y_tgt = MathTex(r"y", font_size=38, color=GREEN).move_to(tgt_node)

        arrow = DoubleArrow(out_pos + RIGHT * 0.45, tgt_pos + LEFT * 0.45,
                            color=RED, stroke_width=4, buff=0)
        delta_label = MathTex(r"\hat{y} - y", font_size=34, color=RED).next_to(arrow, UP, buff=0.25)

        loss_eq = MathTex(
            r"L = \tfrac{1}{2}(\hat{y} - y)^2",
            font_size=48, color=GOLD,
        ).shift(DOWN * 1.2)

        box = SurroundingRectangle(loss_eq, color=GOLD, buff=0.2, stroke_width=2)

        self.play(FadeIn(b), FadeIn(label),
                  GrowFromCenter(out_node), GrowFromCenter(tgt_node),
                  FadeIn(y_hat), FadeIn(y_tgt), run_time=1)
        self.play(GrowArrow(arrow), Write(delta_label), run_time=0.8)
        self.play(Write(loss_eq), Create(box), run_time=1)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 4 — NAIVE GRADIENT: highlight every weight one by one (costly)
    # ══════════════════════════════════════════════════════════════════════
    def scene_naive(self):
        b     = brand()
        label = Text("Descenso del gradiente ingenuo", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        layers, edges, all_n, all_e = self.make_network(
            [2, 3, 3, 2], center=UP * 0.4, h_gap=2.0, v_gap=0.8
        )

        cost_label = MathTex(r"\mathcal{O}(w^2)", font_size=52, color=RED).shift(DOWN * 2)

        self.play(FadeIn(b), FadeIn(label), Create(all_e), FadeIn(all_n), run_time=1)

        # Highlight each edge one by one (show the cost)
        counter_val = [0]
        counter_tex = Integer(0, font_size=30, color=LGOLD).next_to(cost_label, RIGHT, buff=0.4)
        self.play(FadeIn(cost_label), FadeIn(counter_tex), run_time=0.6)

        for i, e in enumerate(edges[:12]):  # show a subset for time
            self.play(
                e.animate.set_stroke(RED, width=4, opacity=1),
                run_time=0.12,
            )
            self.play(
                e.animate.set_stroke(GOLD, width=0.8, opacity=0.35),
                ChangeDecimalToValue(counter_tex, i + 1),
                run_time=0.10,
            )

        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 5 — CHAIN RULE: function composition as colored boxes
    # ══════════════════════════════════════════════════════════════════════
    def scene_chain(self):
        b     = brand()
        label = Text("Regla de la cadena", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        # f∘g∘h as nested / sequential colored blocks
        colors = [BLUE, PURPLE, TEAL, GOLD]
        func_chars = [r"h", r"g", r"f", r"L"]
        boxes = VGroup()
        arrows_chain = VGroup()

        for i, (col, ch) in enumerate(zip(colors, func_chars)):
            rect = RoundedRectangle(width=1.2, height=1.2, corner_radius=0.15,
                                    fill_color=col, fill_opacity=0.25, stroke_color=col,
                                    stroke_width=2.5)
            rect.shift(RIGHT * (i - 1.5) * 1.8)
            label_f = MathTex(ch, font_size=40, color=col).move_to(rect)
            boxes.add(VGroup(rect, label_f))

        for i in range(len(boxes) - 1):
            a = Arrow(boxes[i].get_right(), boxes[i + 1].get_left(),
                      color=WHITE, stroke_width=2, buff=0.1, max_tip_length_to_length_ratio=0.25)
            arrows_chain.add(a)

        composition = MathTex(
            r"L = f \circ g \circ h",
            font_size=40, color=WHITE,
        ).shift(UP * 2)

        chain_rule = MathTex(
            r"\frac{dL}{dx} = \frac{dL}{df}\cdot\frac{df}{dg}\cdot\frac{dg}{dh}",
            font_size=38, color=GOLD,
        ).shift(DOWN * 1.8)

        self.play(FadeIn(b), FadeIn(label), Write(composition), run_time=0.8)
        self.play(
            LaggedStart(*[GrowFromCenter(box) for box in boxes], lag_ratio=0.3),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_chain], lag_ratio=0.3),
            run_time=0.8,
        )
        self.play(Write(chain_rule), run_time=1.2)

        # Show that gradient flows backward — reverse arrows flash
        back_arrows = VGroup(*[
            Arrow(arrows_chain[i].get_end(), arrows_chain[i].get_start(),
                  color=GOLD, stroke_width=3.5, buff=0.1,
                  max_tip_length_to_length_ratio=0.3).shift(DOWN * 0.45)
            for i in range(len(arrows_chain))
        ])
        self.play(
            LaggedStart(*[GrowArrow(a) for a in reversed(list(back_arrows))], lag_ratio=0.3),
            run_time=1,
        )
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 6 — DELTA SIGNALS: gradient propagates backward, color=reuse
    # ══════════════════════════════════════════════════════════════════════
    def scene_backprop(self):
        b     = brand()
        label = Text("Backpropagation", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        layers, edges, all_n, all_e = self.make_network(
            [3, 4, 4, 2], center=UP * 0.3, h_gap=2.2, v_gap=0.75
        )

        # Layer labels
        layer_names = ["input", "hidden", "hidden", "output"]
        l_labels = VGroup()
        for li, (layer, name) in enumerate(zip(layers, layer_names)):
            top = max(n.get_top()[1] for n in layer)
            lbl = Text(name, font_size=16, color=LGOLD).move_to(
                np.array([layer[0].get_center()[0], top + 0.45, 0])
            )
            l_labels.add(lbl)

        delta_colors = [RED, PURPLE, BLUE, TEAL]  # one per layer (right to left)

        self.play(FadeIn(b), FadeIn(label), Create(all_e), FadeIn(all_n),
                  FadeIn(l_labels), run_time=1.2)

        # Forward pass (quick, blue)
        self.play(
            *[n.animate.set_fill(BLUE, opacity=0.5) for layer in layers for n in layer],
            run_time=0.6,
        )
        self.play(
            *[n.animate.set_fill(DARK, opacity=1) for layer in layers for n in layer],
            run_time=0.4,
        )

        # Backward pass: color waves from right to left
        for li in range(len(layers) - 1, -1, -1):
            col = delta_colors[li]
            layer = layers[li]

            # Build delta label above this layer
            delta_sym = MathTex(r"\delta_{" + str(li + 1) + r"}", font_size=30, color=col)
            delta_sym.next_to(l_labels[li], DOWN, buff=0.2)

            # Highlight edges feeding INTO this layer (from li+1) or from li
            relevant_edges = []
            if li < len(layers) - 1:
                for e in edges:
                    # edges going FROM li TO li+1
                    if any(np.allclose(e.get_start(), n.get_center(), atol=0.05) for n in layer):
                        relevant_edges.append(e)

            anims = [n.animate.set_fill(col, opacity=0.75).set_stroke(col, width=4)
                     for n in layer]
            if relevant_edges:
                anims += [e.animate.set_stroke(col, width=2.5, opacity=0.9)
                          for e in relevant_edges]
            anims.append(FadeIn(delta_sym))

            self.play(*anims, run_time=0.55)
            self.wait(0.25)

            # Fade back slightly but keep delta label
            self.play(
                *[n.animate.set_fill(col, opacity=0.25).set_stroke(col, width=2) for n in layer],
                *([e.animate.set_stroke(col, width=1.2, opacity=0.55) for e in relevant_edges]),
                run_time=0.3,
            )

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 7 — REUSE: same delta block shared across layers
    # ══════════════════════════════════════════════════════════════════════
    def scene_reuse(self):
        b     = brand()
        label = Text("Reutilización de cálculos", font_size=22, color=GOLD).to_edge(DOWN, buff=0.4)

        # Two derivative equations, highlighting the shared prefix
        eq1 = MathTex(
            r"\frac{\partial L}{\partial w_2}",
            r"=",
            r"\underbrace{(\hat{y}-y)\,\sigma'(a_2)}_{\delta_2}",
            r"\cdot\, z_1",
            font_size=34, color=WHITE,
        ).shift(UP * 1.4)

        eq2 = MathTex(
            r"\frac{\partial L}{\partial w_1}",
            r"=",
            r"\underbrace{(\hat{y}-y)\,\sigma'(a_2)}_{\delta_2}",
            r"\cdot\,w_2\,\sigma'(a_1)\,x",
            font_size=34, color=WHITE,
        ).shift(DOWN * 0.3)

        # Color the shared delta part
        for eq in (eq1, eq2):
            eq[2].set_color(GOLD)

        # Brace linking them
        brace_group = BraceBetweenPoints(
            eq1[2].get_left() + LEFT * 0.1,
            eq2[2].get_left() + LEFT * 0.1,
            direction=LEFT, color=GOLD,
        )
        reuse_tag = Text("mismo\ncálculo", font_size=20, color=GOLD,
                          line_spacing=1.2).next_to(brace_group, LEFT, buff=0.2)

        ow_label = MathTex(r"\mathcal{O}(w)", font_size=52, color=GREEN).shift(DOWN * 2.2)

        self.play(FadeIn(b), FadeIn(label), Write(eq1), run_time=1)
        self.play(Write(eq2), run_time=1)
        self.play(Create(brace_group), FadeIn(reuse_tag), run_time=0.8)
        self.play(Write(ow_label), run_time=0.8)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 8 — EFFICIENCY: O(w²) vs O(w) visual dot comparison
    # ══════════════════════════════════════════════════════════════════════
    def scene_efficiency(self):
        b     = brand()

        left_center  = LEFT * 3
        right_center = RIGHT * 3
        n_dots = 16  # simulate w = 16

        # O(w²) grid: n×n dots
        def dot_grid(cx, rows, cols, col_fill, spacing=0.32):
            dots = VGroup()
            for r in range(rows):
                for c in range(cols):
                    x = cx + (c - cols / 2 + 0.5) * spacing
                    y = (r - rows / 2 + 0.5) * spacing + 0.3
                    d = Dot([x, y, 0], radius=0.06, color=col_fill)
                    dots.add(d)
            return dots

        n = 8
        bad_dots  = dot_grid(left_center[0],  n, n, RED)
        good_dots = dot_grid(right_center[0], 1, n * n, GREEN, spacing=0.28)

        bad_label  = MathTex(r"\mathcal{O}(w^2)", font_size=44, color=RED ).next_to(bad_dots,  UP, buff=0.4)
        good_label = MathTex(r"\mathcal{O}(w)",   font_size=44, color=GREEN).next_to(good_dots, UP, buff=0.4)

        bad_name  = Text("Gradiente ingenuo",  font_size=20, color=RED ).next_to(bad_dots,  DOWN, buff=0.4)
        good_name = Text("Backpropagation",    font_size=20, color=GREEN).next_to(good_dots, DOWN, buff=0.4)

        vs = Text("VS", font_size=32, color=WHITE, weight=BOLD)

        self.play(FadeIn(b), run_time=0.4)
        self.play(
            LaggedStart(*[GrowFromCenter(d) for d in bad_dots],  lag_ratio=0.01),
            Write(bad_label), FadeIn(bad_name),
            run_time=1.5,
        )
        self.play(FadeIn(vs), run_time=0.4)
        self.play(
            LaggedStart(*[GrowFromCenter(d) for d in good_dots], lag_ratio=0.005),
            Write(good_label), FadeIn(good_name),
            run_time=1.2,
        )
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)

    # ══════════════════════════════════════════════════════════════════════
    # Scene 9 — CLOSING: pulsing network + brand
    # ══════════════════════════════════════════════════════════════════════
    def scene_closing(self):
        layers, edges, all_n, all_e = self.make_network(
            [3, 5, 5, 5, 3], center=UP * 0.5, h_gap=1.9, v_gap=0.7, r=0.22
        )

        brand_big = Text("ATARRAIA", font_size=64, color=GOLD, weight=BOLD).to_edge(DOWN, buff=0.6)
        sub       = Text("Semillero de Redes Neuronales", font_size=22, color=WHITE).next_to(brand_big, UP, buff=0.15)

        self.play(Create(all_e, lag_ratio=0.02), FadeIn(all_n, lag_ratio=0.02), run_time=1.4)
        self.play(Write(brand_big), FadeIn(sub), run_time=1)

        # Pulse the whole network three times
        pulse_colors = [BLUE, PURPLE, GOLD]
        for col in pulse_colors:
            self.play(
                *[n.animate.set_fill(col, opacity=0.7).set_stroke(col, width=3.5) for n in all_n],
                *[e.animate.set_stroke(col, width=1.5, opacity=0.7) for e in edges],
                run_time=0.5,
            )
            self.play(
                *[n.animate.set_fill(DARK, opacity=1).set_stroke(GOLD, width=2.5) for n in all_n],
                *[e.animate.set_stroke(GOLD, width=0.8, opacity=0.35) for e in edges],
                run_time=0.5,
            )

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)

    # ── Construct ──────────────────────────────────────────────────────
    def construct(self):
        self.scene_title()
        self.scene_forward()
        self.scene_loss()
        self.scene_naive()
        self.scene_chain()
        self.scene_backprop()
        self.scene_reuse()
        self.scene_efficiency()
        self.scene_closing()
