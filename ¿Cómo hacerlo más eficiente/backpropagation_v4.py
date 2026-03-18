"""
backpropagation_v4.py — "REVERSE"
==================================
A visual film about backpropagation. ~195s total.

Visual innovations vs v1–v3:
  • Vertical network (input TOP, output BOTTOM — data falls like rain)
  • Hexagonal neurons with concentric glow rings
  • Particle streams spreading between layers
  • Chain rule decomposed as three physical operations inside a neuron
  • Gradient heat map: every edge recolored by attribution magnitude
  • Topographic loss landscape with gradient descent path

Scene plan:
  1  THE ARCHITECT   22s   Vertical network assembles from void
  2  RAINFALL        25s   Data particles fall through layers
  3  JUDGEMENT       18s   Prediction vs target, error blooms
  4  THE REVERSE     38s   Gradient rises — plus slow-motion chain-rule zoom
  5  THE X-RAY       22s   Every edge colored by gradient magnitude
  6  THE LANDSCAPE   25s   Loss contour map, gradient arrows, descent path
  7  ITERATION       28s   Training loop, live loss curve, network learns
  8  EQUILIBRIUM     17s   Network blooms green → constellation → brand
"""

from manim import *
import numpy as np

# ── Palette ──────────────────────────────────────────────────────────────────
VOID      = "#000205"
BIOLUM    = "#00ffd5"
EMBER     = "#ff4500"
CHALK     = "#f5f0e8"
MARIGOLD  = "#ffbe00"
VIOLET    = "#9b5de5"
ROSE      = "#ff006e"
GREEN     = "#06d6a0"
BLUE_GRAD = "#3a86ff"
DIM       = "#080820"

np.random.seed(42)


# ── Helpers ───────────────────────────────────────────────────────────────────
def hex_neuron(pos, r=0.22, color=CHALK):
    """
    Hexagonal neuron with 3 concentric glow rings + solid core.
    Indices: [0]=outer glow, [1]=mid glow, [2]=inner ring, [3]=solid core
    """
    g = VGroup()
    for scale, opacity, width in [(2.4, 0.05, 1.0), (1.6, 0.18, 1.5), (1.0, 0.75, 2.0)]:
        ring = RegularPolygon(n=6, start_angle=PI / 6)
        ring.set_width(r * 2 * scale)
        ring.set_stroke(color=color, opacity=opacity, width=width)
        ring.set_fill(opacity=0)
        ring.move_to(pos)
        g.add(ring)
    core = RegularPolygon(n=6, start_angle=PI / 6)
    core.set_width(r * 2 * 0.6)
    core.set_fill(color=color, opacity=0.4)
    core.set_stroke(width=0)
    core.move_to(pos)
    g.add(core)
    return g


def make_vertical_network(layer_sizes, center=ORIGIN, h_gap=1.1, v_gap=2.0, r=0.22):
    """
    Vertical layout: first layer at top, last at bottom.
    Returns (layers_list, edge_list, all_nodes VGroup, all_edges VGroup).
    """
    n = len(layer_sizes)
    y_pos = [center[1] + (n / 2 - 0.5 - i) * v_gap for i in range(n)]
    layers = []
    for size, y in zip(layer_sizes, y_pos):
        layer = []
        for col in range(size):
            x = center[0] + (col - (size - 1) / 2) * h_gap
            layer.append(hex_neuron(np.array([x, y, 0]), r=r, color=CHALK))
        layers.append(layer)

    edge_list = []
    for i in range(n - 1):
        for ng1 in layers[i]:
            for ng2 in layers[i + 1]:
                p1 = ng1[2].get_center()
                p2 = ng2[2].get_center()
                e = Line(p1, p2, stroke_color=MARIGOLD,
                         stroke_width=0.5, stroke_opacity=0.15)
                edge_list.append(e)

    all_n = VGroup(*[g for layer in layers for g in layer])
    all_e = VGroup(*edge_list)
    return layers, edge_list, all_n, all_e


def make_brand():
    return Text("A T A R R A I A", font_size=16, color=MARIGOLD).to_corner(UL, buff=0.35)


# ── Main class ────────────────────────────────────────────────────────────────
class BackpropagationV4(Scene):

    def setup(self):
        self.camera.background_color = VOID

    # ══════════════════════════════════════════════════════════════════════════
    # 1 — THE ARCHITECT  (22s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_architect(self):
        b = make_brand()
        layers, edges, all_nodes, all_edges = make_vertical_network(
            [3, 5, 5, 2], h_gap=1.1, v_gap=2.0, r=0.22
        )
        self._layers    = layers
        self._edges     = edges
        self._all_nodes = all_nodes
        self._all_edges = all_edges

        self.wait(1.5)
        self.play(FadeIn(b), run_time=0.6)

        # Layers nucleate top to bottom
        for layer in layers:
            self.play(
                LaggedStart(*[GrowFromCenter(ng) for ng in layer], lag_ratio=0.18),
                run_time=1.4,
            )
            self.wait(0.2)

        # Fine gold threads descend between layers
        self.play(Create(all_edges, lag_ratio=0.012), run_time=2.8)
        self.wait(1.5)

        # Network breathes — five slow pulses
        for _ in range(5):
            self.play(
                *[ng[2].animate.set_stroke(CHALK, opacity=1.0, width=3.5) for ng in all_nodes],
                run_time=0.75, rate_func=there_and_back,
            )
            self.wait(0.65)

        self.wait(3.0)

    # ══════════════════════════════════════════════════════════════════════════
    # 2 — RAINFALL  (25s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_rainfall(self):
        layers    = self._layers
        edges     = self._edges
        all_nodes = self._all_nodes

        # Input layer sparkles
        self.play(
            *[ng[3].animate.set_fill(BIOLUM, opacity=0.9) for ng in layers[0]],
            *[ng[2].animate.set_stroke(BIOLUM, opacity=0.9, width=3) for ng in layers[0]],
            run_time=1.0,
        )

        # Particles spread from layer centroid downward through each transition
        for li in range(len(layers) - 1):
            src, dst = layers[li], layers[li + 1]

            # Edges for this transition
            out_edges = [
                e for e in edges
                if any(np.allclose(e.get_start(), ng[2].get_center(), atol=0.1)
                       for ng in src)
            ]

            # Particles start at src centroid, fan out to dst neurons
            src_center = np.mean([ng[3].get_center() for ng in src], axis=0)
            particles = VGroup(*[
                Dot(src_center, radius=0.07, color=BIOLUM, fill_opacity=0.95)
                for _ in dst
            ])
            self.add(particles)

            self.play(
                *[e.animate.set_stroke(BIOLUM, width=2.0, opacity=0.7) for e in out_edges],
                *[particles[j].animate.move_to(dst[j][3].get_center())
                  for j in range(len(dst))],
                run_time=1.2,
            )
            self.play(
                *[ng[3].animate.set_fill(BIOLUM, opacity=0.85) for ng in dst],
                *[ng[2].animate.set_stroke(BIOLUM, opacity=0.9, width=3) for ng in dst],
                *[ng[3].animate.set_fill(CHALK,  opacity=0.35) for ng in src],
                *[ng[2].animate.set_stroke(CHALK, opacity=0.6,  width=2) for ng in src],
                *[e.animate.set_stroke(MARIGOLD, width=0.5, opacity=0.15) for e in out_edges],
                FadeOut(particles),
                run_time=0.7,
            )
            self.wait(0.3)

        # Prediction dot + target dot appear below output layer
        out_center = np.mean([ng[3].get_center() for ng in layers[-1]], axis=0)
        pred_pos   = out_center + DOWN * 1.0 + LEFT  * 0.4
        tgt_pos    = out_center + DOWN * 1.0 + RIGHT * 0.4

        pred_dot   = Dot(pred_pos, radius=0.14, color=BIOLUM, fill_opacity=1.0)
        tgt_dot    = Dot(tgt_pos,  radius=0.14, color=ROSE,   fill_opacity=1.0)
        pred_ring  = Circle(radius=0.24, stroke_color=BIOLUM, stroke_opacity=0.5,
                            fill_opacity=0).move_to(pred_pos)
        tgt_ring   = Circle(radius=0.24, stroke_color=ROSE, stroke_opacity=0.5,
                            fill_opacity=0).move_to(tgt_pos)

        self.play(
            *[ng[3].animate.set_fill(CHALK, opacity=0.35) for ng in layers[-1]],
            *[ng[2].animate.set_stroke(CHALK, opacity=0.6,  width=2) for ng in layers[-1]],
            GrowFromCenter(pred_dot), GrowFromCenter(pred_ring),
            run_time=1.0,
        )
        self.play(GrowFromCenter(tgt_dot), GrowFromCenter(tgt_ring), run_time=0.8)

        # Two dots orbit each other, never quite meeting
        for _ in range(2):
            self.play(
                pred_dot.animate.shift(RIGHT * 0.14 + DOWN * 0.08),
                pred_ring.animate.shift(RIGHT * 0.14 + DOWN * 0.08),
                run_time=0.65, rate_func=there_and_back,
            )

        self.wait(8.5)

        self._pred_dot  = pred_dot
        self._tgt_dot   = tgt_dot
        self._pred_ring = pred_ring
        self._tgt_ring  = tgt_ring

    # ══════════════════════════════════════════════════════════════════════════
    # 3 — JUDGEMENT  (18s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_judgement(self):
        pred_dot  = self._pred_dot
        tgt_dot   = self._tgt_dot
        all_nodes = self._all_nodes

        # Dots collide and bounce
        mid = (pred_dot.get_center() + tgt_dot.get_center()) / 2
        self.play(
            pred_dot.animate.move_to(mid + LEFT * 0.06),
            tgt_dot.animate.move_to(mid + RIGHT * 0.06),
            run_time=0.8,
        )
        self.play(
            pred_dot.animate.move_to(self._pred_dot.get_center() + LEFT * 0.32),
            tgt_dot.animate.move_to(self._tgt_dot.get_center()  + RIGHT * 0.32),
            run_time=0.5, rate_func=rush_into,
        )

        # Red arc between them
        arc = Line(pred_dot.get_center(), tgt_dot.get_center(),
                   stroke_color=EMBER, stroke_width=4)
        self.play(Create(arc), run_time=0.5)

        # "L" rises
        loss_sym = MathTex(r"L", font_size=96, color=EMBER)
        loss_sym.next_to(arc, UP, buff=0.3)
        self.play(FadeIn(loss_sym, scale=0.2), run_time=1.0)
        self.play(loss_sym.animate.scale(1.5), run_time=0.45, rate_func=there_and_back)
        self.play(loss_sym.animate.scale(1.5), run_time=0.45, rate_func=there_and_back)

        # Shockwave rings expand upward from the error
        error_center = arc.get_center()
        for radius_target in [1.5, 3.0, 5.5]:
            ring = Circle(radius=0.1, stroke_color=EMBER,
                          stroke_opacity=0.55, stroke_width=2.0,
                          fill_opacity=0).move_to(error_center)
            self.add(ring)
            self.play(
                ring.animate.scale(radius_target / 0.1).set_stroke(opacity=0),
                run_time=0.9, rate_func=smooth,
            )
            self.remove(ring)

        # Network flashes red
        self.play(
            *[ng[3].animate.set_fill(EMBER, opacity=0.65) for ng in all_nodes],
            *[ng[2].animate.set_stroke(EMBER, opacity=0.75, width=3) for ng in all_nodes],
            run_time=0.9,
        )
        self.play(
            *[ng[3].animate.set_fill(CHALK, opacity=0.3) for ng in all_nodes],
            *[ng[2].animate.set_stroke(CHALK, opacity=0.55, width=2) for ng in all_nodes],
            run_time=1.4,
        )

        # L shrinks to corner as a reminder
        self.play(
            loss_sym.animate.scale(0.25).to_corner(UR, buff=0.35),
            FadeOut(arc),
            FadeOut(self._pred_ring), FadeOut(self._tgt_ring),
            run_time=1.2,
        )

        self.wait(7.0)
        self._loss_sym = loss_sym

    # ══════════════════════════════════════════════════════════════════════════
    # 4 — THE REVERSE  (38s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_reverse(self):
        layers    = self._layers
        edges     = self._edges
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        # Gradient colors: output=ROSE, hidden layers=intermediate, input=warm gold
        grad_colors = [MARIGOLD, "#ff8c00", EMBER, ROSE]  # index 0=input, 3=output

        delta_labels = []

        # Sweep UPWARD: output → input
        for li in range(len(layers) - 1, -1, -1):
            col   = grad_colors[li]
            layer = layers[li]

            # Edges whose END is in this layer (incoming from below = going upward)
            up_edges = []
            if li > 0:
                up_edges = [
                    e for e in edges
                    if any(np.allclose(e.get_end(), ng[2].get_center(), atol=0.1)
                           for ng in layer)
                ]

            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.9) for ng in layer],
                *[ng[2].animate.set_stroke(col, opacity=1.0, width=3.5) for ng in layer],
                *([e.animate.set_stroke(col, width=2.2, opacity=0.8) for e in up_edges]),
                run_time=1.2,
            )

            # δ symbol at this layer
            x_avg = np.mean([ng[2].get_center()[0] for ng in layer])
            y_top = max(ng[2].get_center()[1]      for ng in layer)
            dsym  = MathTex(r"\delta_{" + str(li + 1) + r"}", font_size=36, color=col)
            dsym.move_to(np.array([x_avg, y_top + 0.58, 0]))
            self.play(FadeIn(dsym, scale=0.25), run_time=0.5)
            delta_labels.append(dsym)
            self.wait(0.35)

        self.wait(2.0)

        # ── Slow-motion ZOOM: chain rule inside one neuron ────────────────────
        focus = layers[1][2]   # middle neuron, hidden layer 1

        # Dim everything else
        non_focus = VGroup(*[
            ng for li, layer in enumerate(layers)
            for ng in layer if ng is not focus
        ])
        self.play(
            *[FadeOut(d) for d in delta_labels],
            non_focus.animate.set_stroke(opacity=0.08).set_fill(opacity=0.05),
            all_edges.animate.set_stroke(opacity=0.04),
            FadeOut(self._pred_dot), FadeOut(self._tgt_dot),
            run_time=1.8,
        )

        # Enlarged ghost neuron at center
        ghost = hex_neuron(ORIGIN, r=0.55, color=grad_colors[1])
        ghost[3].set_fill(grad_colors[1], opacity=0.5)
        self.play(FadeIn(ghost, scale=0.3), run_time=1.0)

        # Chain rule diagram: δ_{l+1} → [×σ'(a)] → [×w] → δ_l
        right_x, left_x = 3.8, -3.8

        d_right = MathTex(r"\delta_{l+1}", font_size=36, color=ROSE
                          ).move_to(RIGHT * right_x)
        d_left  = MathTex(r"\delta_l",     font_size=36, color=MARIGOLD
                          ).move_to(LEFT  * left_x)

        sig_rect = RoundedRectangle(width=2.0, height=0.9, corner_radius=0.2,
                                    fill_color=DIM, fill_opacity=0.95,
                                    stroke_color=VIOLET, stroke_width=2.5
                                    ).shift(RIGHT * 1.3)
        sig_lbl  = MathTex(r"\times\,\sigma'(a_l)", font_size=27, color=VIOLET
                           ).move_to(sig_rect)
        sig_grp  = VGroup(sig_rect, sig_lbl)

        w_rect   = RoundedRectangle(width=1.6, height=0.9, corner_radius=0.2,
                                    fill_color=DIM, fill_opacity=0.95,
                                    stroke_color=MARIGOLD, stroke_width=2.5
                                    ).shift(LEFT * 1.3)
        w_lbl    = MathTex(r"\times\,w_{ij}", font_size=27, color=MARIGOLD
                           ).move_to(w_rect)
        w_grp    = VGroup(w_rect, w_lbl)

        kw = dict(stroke_width=2.5, buff=0.12, max_tip_length_to_length_ratio=0.22)
        a1 = Arrow(d_right.get_left(), sig_grp.get_right(), color=ROSE, **kw)
        a2 = Arrow(sig_grp.get_left(), w_grp.get_right(),   color=EMBER, **kw)
        a3 = Arrow(w_grp.get_left(),   d_left.get_right(),  color=MARIGOLD, **kw)

        # Reveal the diagram piece by piece
        self.play(FadeIn(d_right, shift=LEFT * 0.4), run_time=0.8)
        self.play(GrowArrow(a1), GrowFromCenter(sig_grp), run_time=0.9)
        self.play(GrowArrow(a2), GrowFromCenter(w_grp),   run_time=0.9)
        self.play(GrowArrow(a3), FadeIn(d_left, shift=RIGHT * 0.4), run_time=0.9)

        self.wait(6.0)

        chain_group = VGroup(d_right, d_left, sig_grp, w_grp, a1, a2, a3)

        # Restore network, fade chain rule
        self.play(
            FadeOut(chain_group), FadeOut(ghost),
            non_focus.animate.set_stroke(CHALK, opacity=0.55).set_fill(CHALK, opacity=0.35),
            all_edges.animate.set_stroke(MARIGOLD, opacity=0.15),
            run_time=2.0,
        )

        # Quick second backward sweep to close scene
        for li in range(len(layers) - 1, -1, -1):
            col = grad_colors[li]
            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.75) for ng in layers[li]],
                run_time=0.55,
            )
            self.wait(0.2)

        self.wait(5.0)

    # ══════════════════════════════════════════════════════════════════════════
    # 5 — THE X-RAY  (22s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_xray(self):
        edges     = self._edges
        all_nodes = self._all_nodes

        # Assign simulated gradient values (seeded, so visual is consistent)
        np.random.seed(13)
        grad_vals = np.random.uniform(-1, 1, len(edges))
        grad_vals /= np.abs(grad_vals).max()

        # Fade neurons to near-black silhouette
        self.play(
            *[ng[3].animate.set_fill(CHALK, opacity=0.15) for ng in all_nodes],
            *[ng[2].animate.set_stroke(CHALK, opacity=0.3) for ng in all_nodes],
            run_time=1.5,
        )

        # Color edges by gradient: BLUE_GRAD (negative) → EMBER (positive)
        _grad_palette = color_gradient([BLUE_GRAD, EMBER], 101)
        edge_anims = []
        for e, g in zip(edges, grad_vals):
            alpha = (g + 1) / 2
            col   = _grad_palette[int(alpha * 100)]
            wid   = 0.5 + 3.0 * abs(g)
            edge_anims.append(e.animate.set_stroke(col, width=wid, opacity=0.9))

        self.play(*edge_anims, run_time=2.5)

        # Legend
        bar_neg = Rectangle(width=2.0, height=0.2,
                             fill_color=BLUE_GRAD, fill_opacity=0.9, stroke_width=0)
        bar_pos = Rectangle(width=2.0, height=0.2,
                             fill_color=EMBER, fill_opacity=0.9, stroke_width=0)
        bar_pos.next_to(bar_neg, RIGHT, buff=0.06)
        lbl_neg = Text("↓ decrease", font_size=17, color=BLUE_GRAD
                       ).next_to(bar_neg, DOWN, buff=0.14)
        lbl_pos = Text("↑ increase", font_size=17, color=EMBER
                       ).next_to(bar_pos, DOWN, buff=0.14)
        legend  = VGroup(bar_neg, bar_pos, lbl_neg, lbl_pos).to_edge(DOWN, buff=0.55)

        self.play(FadeIn(legend, shift=UP * 0.2), run_time=1.0)
        self.wait(8.5)
        self.play(FadeOut(legend), run_time=1.0)

        # Reset edges for next scene
        self.play(
            *[e.animate.set_stroke(MARIGOLD, width=0.5, opacity=0.15) for e in edges],
            *[ng[3].animate.set_fill(CHALK, opacity=0.4)  for ng in all_nodes],
            *[ng[2].animate.set_stroke(CHALK, opacity=0.6) for ng in all_nodes],
            run_time=2.0,
        )
        self.wait(1.5)

    # ══════════════════════════════════════════════════════════════════════════
    # 6 — THE LANDSCAPE  (25s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_landscape(self):
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        self.play(
            FadeOut(all_nodes), FadeOut(all_edges), FadeOut(self._loss_sym),
            run_time=1.5,
        )

        # Topographic contour map of L(w₁, w₂)
        # Minimum sits at (1.3, -1.0) in screen coords
        cx, cy = 1.3, -1.0

        level_colors = color_gradient([EMBER, BIOLUM], 7)
        contours = VGroup()
        for i, col in enumerate(level_colors):
            rx = (3.0 - i * 0.37) * 1.2
            ry = (3.0 - i * 0.37) * 0.75
            ellipse = Ellipse(width=rx * 2, height=ry * 2,
                              stroke_color=col, stroke_opacity=0.55,
                              stroke_width=1.5, fill_opacity=0)
            ellipse.shift(np.array([cx - 0.5, cy + 0.3, 0]))
            contours.add(ellipse)

        # Axis labels
        w1_lbl = MathTex("w_1", font_size=30, color=CHALK
                         ).set_opacity(0.4).to_edge(RIGHT, buff=0.5).shift(DOWN * 3.5)
        w2_lbl = MathTex("w_2", font_size=30, color=CHALK
                         ).set_opacity(0.4).to_edge(UP, buff=0.5).shift(LEFT * 6.0)

        # Minimum star
        min_pt  = np.array([cx, cy, 0])
        min_dot = Dot(min_pt, radius=0.12, color=BIOLUM, fill_opacity=0.9)
        min_ring = Circle(radius=0.22, stroke_color=BIOLUM,
                          stroke_opacity=0.6, fill_opacity=0).move_to(min_pt)

        # Starting position (high loss, outer ring)
        start = np.array([-2.0, 2.0, 0])
        curr  = Dot(start, radius=0.15, color=CHALK, fill_opacity=1.0)

        self.play(
            LaggedStart(*[Create(c) for c in contours], lag_ratio=0.12),
            FadeIn(w1_lbl), FadeIn(w2_lbl),
            run_time=2.5,
        )
        self.play(GrowFromCenter(min_dot), Create(min_ring), run_time=0.8)
        self.play(GrowFromCenter(curr), run_time=0.7)

        # Gradient arrow (uphill) and neg-gradient arrow (our step)
        direction = start - min_pt
        direction = direction / np.linalg.norm(direction) * 1.1
        grad_arr = Arrow(start, start + direction, color=EMBER,
                         stroke_width=3, buff=0,
                         max_tip_length_to_length_ratio=0.22)
        step_arr = Arrow(start, start - direction * 0.8, color=BIOLUM,
                         stroke_width=3, buff=0,
                         max_tip_length_to_length_ratio=0.22)
        grad_lbl = MathTex(r"\nabla L", font_size=28, color=EMBER
                           ).next_to(grad_arr.get_end(), RIGHT, buff=0.12)
        step_lbl = MathTex(r"-\eta\nabla L", font_size=28, color=BIOLUM
                           ).next_to(step_arr.get_end(), LEFT, buff=0.12)

        self.play(GrowArrow(grad_arr), FadeIn(grad_lbl), run_time=0.8)
        self.play(GrowArrow(step_arr), FadeIn(step_lbl), run_time=0.8)
        self.wait(1.5)

        self.play(FadeOut(grad_arr), FadeOut(grad_lbl),
                  FadeOut(step_arr), FadeOut(step_lbl), run_time=0.7)

        # Gradient descent path — smooth spiral converging on minimum
        n_steps = 50
        path_pts = []
        pos = start.copy()
        for k in range(n_steps):
            t = k / n_steps
            # simple fake gradient: direction toward minimum + small oscillation
            grad = (pos[:2] - min_pt[:2]) * 0.18
            grad += np.array([np.sin(k * 0.8) * 0.06 * (1 - t),
                               np.cos(k * 0.8) * 0.06 * (1 - t)])
            pos[:2] -= grad
            path_pts.append(pos.copy())

        descent = VMobject(stroke_color=MARIGOLD, stroke_width=2.5, stroke_opacity=0.9)
        descent.set_points_smoothly(path_pts)

        self.play(Create(descent), run_time=3.0, rate_func=smooth)
        self.play(curr.animate.move_to(min_pt + np.array([0.04, 0.04, 0])),
                  run_time=1.2)
        self.play(min_ring.animate.scale(1.8).set_stroke(opacity=0),
                  run_time=0.9, rate_func=smooth)

        self.wait(8.0)

        self.play(
            FadeOut(contours), FadeOut(min_dot), FadeOut(descent),
            FadeOut(curr), FadeOut(w1_lbl), FadeOut(w2_lbl),
            run_time=1.5,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # 7 — ITERATION  (28s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_iteration(self):
        # Rebuild network
        layers, edges, all_nodes, all_edges = make_vertical_network(
            [3, 5, 5, 2], h_gap=1.1, v_gap=2.0, r=0.22
        )
        self._layers    = layers
        self._edges     = edges
        self._all_nodes = all_nodes
        self._all_edges = all_edges

        self.play(FadeIn(all_edges), FadeIn(all_nodes, lag_ratio=0.03), run_time=1.5)

        # Live loss axes — top-right corner
        ax = Axes(
            x_range=[0, 8, 1], y_range=[0, 1.0, 0.5],
            x_length=3.2, y_length=1.8,
            axis_config={"color": CHALK, "stroke_opacity": 0.35, "stroke_width": 1.0},
            tips=False,
        ).to_corner(UR, buff=0.45)
        loss_label = Text("L", font_size=18, color=EMBER).next_to(ax, UP, buff=0.05)

        self.play(Create(ax), FadeIn(loss_label), run_time=1.0)

        loss_fn  = lambda t: 0.85 * np.exp(-0.55 * t) + 0.08
        grad_c   = [MARIGOLD, "#ff8c00", EMBER, ROSE]

        # Build loss curve cumulatively over 2 cycles (each covering t=0..4 and t=4..8)
        t_segments = [(0, 4.0), (4.0, 8.0)]
        curve_pts   = []

        for cycle, (t0, t1) in enumerate(t_segments):
            # Forward sweep
            for li, layer in enumerate(layers):
                out_e = [
                    e for e in edges
                    if li < len(layers) - 1 and any(
                        np.allclose(e.get_start(), ng[2].get_center(), atol=0.1)
                        for ng in layer
                    )
                ]
                self.play(
                    *[ng[3].animate.set_fill(BIOLUM, opacity=0.75) for ng in layer],
                    *([e.animate.set_stroke(BIOLUM, width=1.8, opacity=0.65) for e in out_e]),
                    run_time=0.38,
                )
                self.play(
                    *[ng[3].animate.set_fill(CHALK, opacity=0.3) for ng in layer],
                    *([e.animate.set_stroke(MARIGOLD, width=0.5, opacity=0.15) for e in out_e]),
                    run_time=0.22,
                )

            # Grow loss curve segment
            new_pts = [ax.coords_to_point(t, loss_fn(t))
                       for t in np.linspace(t0, t1, 18)]
            curve_pts.extend(new_pts)
            seg = VMobject(stroke_color=EMBER, stroke_width=2.2, stroke_opacity=0.9)
            seg.set_points_as_corners(curve_pts if len(curve_pts) >= 2 else curve_pts * 2)
            if cycle == 0:
                self.play(Create(seg), run_time=0.9)
                self._loss_curve = seg
            else:
                new_seg = VMobject(stroke_color=EMBER, stroke_width=2.2, stroke_opacity=0.9)
                new_seg.set_points_as_corners(curve_pts)
                self.play(Transform(self._loss_curve, new_seg), run_time=0.9)

            # Backward sweep
            for li in range(len(layers) - 1, -1, -1):
                up_e = [
                    e for e in edges
                    if li > 0 and any(
                        np.allclose(e.get_end(), ng[2].get_center(), atol=0.1)
                        for ng in layers[li]
                    )
                ]
                self.play(
                    *[ng[3].animate.set_fill(grad_c[li], opacity=0.75) for ng in layers[li]],
                    *([e.animate.set_stroke(grad_c[li], width=1.8, opacity=0.6) for e in up_e]),
                    run_time=0.38,
                )
                self.play(
                    *[ng[3].animate.set_fill(CHALK, opacity=0.3) for ng in layers[li]],
                    *([e.animate.set_stroke(MARIGOLD, width=0.5, opacity=0.15) for e in up_e]),
                    run_time=0.22,
                )

            # Weight update pulse — edges briefly thicken and thin
            self.play(
                *[e.animate.set_stroke(MARIGOLD, width=1.8, opacity=0.5) for e in edges],
                run_time=0.4,
            )
            self.play(
                *[e.animate.set_stroke(MARIGOLD, width=0.5, opacity=0.15) for e in edges],
                run_time=0.3,
            )
            self.wait(0.4)

        # SUCCESS — network blooms GREEN
        self.play(
            *[ng[3].animate.set_fill(GREEN, opacity=0.9) for ng in all_nodes],
            *[ng[2].animate.set_stroke(GREEN, opacity=0.9, width=3.5) for ng in all_nodes],
            *[e.animate.set_stroke(GREEN, width=1.5, opacity=0.6) for e in edges],
            run_time=1.5,
        )
        self.wait(6.5)

    # ══════════════════════════════════════════════════════════════════════════
    # 8 — EQUILIBRIUM  (17s)
    # ══════════════════════════════════════════════════════════════════════════
    def scene_equilibrium(self):
        all_nodes = self._all_nodes
        all_edges = self._all_edges
        layers    = self._layers

        # Network drifts outward → constellation
        self.play(
            all_nodes.animate.scale(1.3, about_point=ORIGIN),
            all_edges.animate.set_stroke(opacity=0.08, width=0.3),
            run_time=2.5, rate_func=smooth,
        )

        # Brand
        brand_txt = Text("A T A R R A I A", font_size=60, color=MARIGOLD, weight=BOLD)
        self.play(FadeIn(brand_txt, scale=0.5), run_time=2.0)

        # One final EMBER backward pulse through the constellation
        for li in range(len(layers) - 1, -1, -1):
            self.play(
                *[ng[2].animate.set_stroke(EMBER, opacity=0.7, width=3.0)
                  for ng in layers[li]],
                run_time=0.45,
            )
            self.play(
                *[ng[2].animate.set_stroke(GREEN, opacity=0.4, width=1.5)
                  for ng in layers[li]],
                run_time=0.35,
            )

        self.wait(4.0)
        self.play(FadeOut(all_nodes), FadeOut(all_edges), run_time=2.5)
        self.play(FadeOut(brand_txt), run_time=1.5)

    # ── Construct ─────────────────────────────────────────────────────────────
    def construct(self):
        self.scene_architect()    # 22s
        self.scene_rainfall()     # 25s
        self.scene_judgement()    # 18s
        self.scene_reverse()      # 38s
        self.scene_xray()         # 22s
        self.scene_landscape()    # 25s
        self.scene_iteration()    # 28s
        self.scene_equilibrium()  # 17s
        # Total: ~195s
