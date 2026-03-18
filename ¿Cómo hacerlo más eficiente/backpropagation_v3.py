"""
backpropagation_v3.py
=====================
Psychedelic, music-synced animation for "Feels Like We Only Go Backwards"
by Tame Impala (~3:12 / 192 seconds total).

Scene timing:
  Scene 1  "THE VOID"          0:00–0:17   17s   (intro)
  Scene 2  "FORWARD"           0:17–0:49   32s   (verse 1)
  Scene 3  "THE ERROR"         0:49–1:06   17s   (pre-chorus 1)
  Scene 4  "GOING BACKWARDS"   1:06–1:41   35s   (chorus 1)
  Scene 5  "CHAIN RULE"        1:41–2:09   28s   (verse 2)
  Scene 6  "EFFICIENCY"        2:09–2:26   17s   (pre-chorus 2)
  Scene 7  "THE CYCLE"         2:26–2:58   32s   (chorus 2)
  Scene 8  "ATARRAIA"          2:58–3:12   14s   (outro)
"""

from manim import *
import numpy as np

# ── Cosmic palette ──────────────────────────────────────────────────────────
VOID    = "#030008"
INDIGO  = "#3d1c8a"
VIOLET  = "#7b2fe0"
MAGENTA = "#d63fcc"
PINK    = "#ff6eb4"
CYAN    = "#00f0e0"
GOLD    = "#e8b825"
LGOLD   = "#f5d56e"
WHITE   = "#f0ecff"
RED     = "#ff4d6d"
GREEN   = "#2ecc71"
DARK    = "#0a0318"

np.random.seed(7)


# ── Helpers ─────────────────────────────────────────────────────────────────
def glow_neuron(center, r=0.22, core_color=VIOLET, layers=3):
    """Return a VGroup of concentric circles simulating a glow bloom."""
    group = VGroup()
    opacities = [0.85, 0.35, 0.12]
    radii_mult = [1.0, 1.6, 2.5]
    for i in range(layers):
        c = Circle(
            radius=r * radii_mult[i],
            stroke_color=core_color,
            stroke_opacity=opacities[i],
            stroke_width=max(1.5, 3.5 - i * 1.0),
            fill_opacity=0.0,
        ).move_to(center)
        group.add(c)
    # Solid core
    core = Circle(
        radius=r * 0.55,
        fill_color=core_color,
        fill_opacity=0.6,
        stroke_width=0,
    ).move_to(center)
    group.add(core)
    return group


def make_network_v3(layer_sizes, center=ORIGIN, h_gap=2.0, v_gap=0.8, r=0.22,
                    node_color=VIOLET, edge_color=INDIGO):
    """Return (layers_list, edge_list, all_nodes VGroup, all_edges VGroup)."""
    layers = []
    for col, n in enumerate(layer_sizes):
        layer = []
        x = (col - (len(layer_sizes) - 1) / 2) * h_gap + center[0]
        for row in range(n):
            y = (row - (n - 1) / 2) * v_gap + center[1]
            g = glow_neuron(np.array([x, y, 0]), r=r, core_color=node_color)
            layer.append(g)
        layers.append(layer)

    edge_list = []
    for i in range(len(layers) - 1):
        for ng1 in layers[i]:
            for ng2 in layers[i + 1]:
                p1 = ng1[0].get_center()
                p2 = ng2[0].get_center()
                e = Line(p1, p2, stroke_color=edge_color,
                         stroke_width=0.6, stroke_opacity=0.25)
                edge_list.append(e)

    all_nodes = VGroup(*[g for layer in layers for g in layer])
    all_edges = VGroup(*edge_list)
    return layers, edge_list, all_nodes, all_edges


class BackpropagationV3(Scene):
    """~192s psychedelic backpropagation animation."""

    def setup(self):
        self.camera.background_color = VOID

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 1 — THE VOID (17s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_void(self):
        # Single neuron pulses in the void
        center_neuron = glow_neuron(ORIGIN, r=0.3, core_color=INDIGO)
        self.play(FadeIn(center_neuron, scale=0.3), run_time=2.5)

        # Pulse it twice (expand outer ring and contract)
        for _ in range(2):
            self.play(
                center_neuron[1].animate.scale(1.4).set_stroke(opacity=0.5),
                run_time=1.0, rate_func=there_and_back,
            )

        # Network materialises from scattered positions
        layers, edges, all_nodes, all_edges = make_network_v3(
            [3, 5, 5, 3], center=ORIGIN + UP * 0.15,
            h_gap=2.2, v_gap=0.75, r=0.22, node_color=INDIGO, edge_color=INDIGO,
        )

        # Scatter starting points
        scatter_offsets = [
            np.array([np.random.uniform(-5, 5), np.random.uniform(-3.5, 3.5), 0])
            for _ in range(len(all_nodes))
        ]
        ghost_nodes = VGroup(*[
            glow_neuron(off, r=0.18, core_color=INDIGO)
            for off in scatter_offsets
        ])

        self.play(FadeOut(center_neuron), FadeIn(ghost_nodes, lag_ratio=0.06), run_time=1.5)

        # Drift to positions
        self.play(
            *[
                ghost_nodes[i].animate.move_to(all_nodes[i][0].get_center())
                for i in range(len(all_nodes))
            ],
            run_time=3.5, rate_func=smooth,
        )

        self.remove(ghost_nodes)
        self.add(all_edges, all_nodes)

        # Draw edges gently
        self.play(
            Create(all_edges, lag_ratio=0.04),
            run_time=3.0,
        )
        self.wait(3.5)  # hold to reach 17s total

        # Store for next scene
        self._layers = layers
        self._edges  = edges
        self._all_nodes = all_nodes
        self._all_edges = all_edges

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 2 — FORWARD (32s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_forward(self):
        layers    = self._layers
        edges     = self._edges
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        # Input symbol
        x_sym = MathTex("x", font_size=42, color=CYAN).next_to(
            layers[0][1][0], LEFT, buff=0.6
        )
        self.play(FadeIn(x_sym, scale=0.5), run_time=1.5)

        # Forward pass — wave of CYAN through layers
        for li, layer in enumerate(layers):
            # Edges leaving this layer
            if li < len(layers) - 1:
                out_edges = [
                    e for e in edges
                    if any(
                        np.allclose(e.get_start(), ng[0].get_center(), atol=0.05)
                        for ng in layer
                    )
                ]
            else:
                out_edges = []

            # Light up neurons CYAN
            self.play(
                *[ng[3].animate.set_fill(CYAN, opacity=0.85) for ng in layer],
                *[ng[0].animate.set_stroke(CYAN, opacity=0.9) for ng in layer],
                run_time=1.2,
                rate_func=smooth,
            )
            self.wait(0.4)

            if out_edges:
                self.play(
                    *[e.animate.set_stroke(CYAN, width=1.8, opacity=0.7) for e in out_edges],
                    run_time=0.8,
                )

            # Dim back to indigo
            self.play(
                *[ng[3].animate.set_fill(INDIGO, opacity=0.6) for ng in layer],
                *[ng[0].animate.set_stroke(INDIGO, opacity=0.85) for ng in layer],
                *([e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in out_edges]),
                run_time=1.0,
            )
            self.wait(0.3)

        # Output symbol
        y_hat = MathTex(r"\hat{y}", font_size=42, color=WHITE).next_to(
            layers[-1][1][0], RIGHT, buff=0.6
        )
        self.play(FadeIn(y_hat, scale=0.5), run_time=1.5)

        # Hold — gently pulse output
        for _ in range(5):
            self.play(
                layers[-1][1][3].animate.set_fill(WHITE, opacity=0.8),
                run_time=0.8, rate_func=there_and_back,
            )
            self.wait(0.6)

        self.wait(4.0)  # pad to ~32s — verse lingers

        self._y_hat  = y_hat
        self._x_sym  = x_sym

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 3 — THE ERROR (17s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_error(self):
        layers    = self._layers
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        out_center = layers[-1][1][0].get_center()

        # Target y appears as ghost circle to the right
        y_pos  = out_center + RIGHT * 1.8
        y_sym  = MathTex("y", font_size=42, color=GREEN).move_to(y_pos)
        target = Circle(radius=0.28, stroke_color=GREEN, stroke_opacity=0.7,
                        fill_opacity=0).move_to(y_pos)

        self.play(FadeIn(target, scale=0.3), FadeIn(y_sym, scale=0.5), run_time=1.5)

        # Red arc showing the gap
        gap_line = Line(out_center + RIGHT * 0.28, y_pos + LEFT * 0.15,
                        color=RED, stroke_width=3)
        self.play(Create(gap_line), run_time=0.8)

        # L symbol blooms
        L_sym = MathTex("L", font_size=72, color=RED).move_to(
            (out_center + y_pos) / 2 + UP * 1.2
        )
        self.play(FadeIn(L_sym, scale=0.2), run_time=1.2)

        # Ripple expands from output node
        for scale_val in [1.5, 2.5, 4.0]:
            ring = Circle(
                radius=0.28 * scale_val, stroke_color=RED,
                stroke_opacity=max(0.05, 0.5 / scale_val), stroke_width=2,
                fill_opacity=0,
            ).move_to(out_center)
            self.play(FadeIn(ring, scale=0.3), run_time=0.5)
            self.play(FadeOut(ring), run_time=0.5)

        # Pulse the whole network red once (error felt everywhere)
        self.play(
            *[ng[0].animate.set_stroke(RED, opacity=0.6) for ng in all_nodes],
            *[e.animate.set_stroke(RED, width=1.0, opacity=0.4) for e in self._edges],
            run_time=1.5,
        )
        self.play(
            *[ng[0].animate.set_stroke(INDIGO, opacity=0.85) for ng in all_nodes],
            *[e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in self._edges],
            run_time=1.5,
        )

        # Clean up extra symbols, keep network
        self.play(
            FadeOut(self._y_hat), FadeOut(self._x_sym),
            FadeOut(gap_line), FadeOut(y_sym), FadeOut(target),
            run_time=1.0,
        )
        # L symbol drifts left to hint at backward direction
        self.play(
            L_sym.animate.shift(LEFT * 1.5).set_color(MAGENTA),
            run_time=2.5, rate_func=smooth,
        )
        self.play(FadeOut(L_sym), run_time=1.0)
        self.wait(3.0)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 4 — GOING BACKWARDS (35s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_backwards(self):
        layers    = self._layers
        edges     = self._edges
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        delta_colors = [PINK, MAGENTA, VIOLET, INDIGO]
        delta_syms = []

        # Gradient wave sweeps RIGHT → LEFT
        for li in range(len(layers) - 1, -1, -1):
            col   = delta_colors[li]
            layer = layers[li]

            # Edges flowing OUT from this layer (toward left)
            in_edges = []
            if li > 0:
                in_edges = [
                    e for e in edges
                    if any(
                        np.allclose(e.get_end(), ng[0].get_center(), atol=0.05)
                        for ng in layer
                    )
                ]

            # Light up neurons
            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.9) for ng in layer],
                *[ng[0].animate.set_stroke(col, opacity=1.0, width=3.5) for ng in layer],
                *([ng[1].animate.set_stroke(col, opacity=0.5) for ng in layer]),
                *([e.animate.set_stroke(col, width=2.5, opacity=0.8) for e in in_edges]),
                run_time=1.4, rate_func=smooth,
            )

            # Delta symbol appears at this layer
            x_pos = layer[0][0].get_center()[0]
            top_y = max(ng[0].get_center()[1] for ng in layer)
            d_sym = MathTex(
                r"\delta_{" + str(li + 1) + r"}",
                font_size=36, color=col,
            ).move_to(np.array([x_pos, top_y + 0.65, 0]))
            self.play(FadeIn(d_sym, scale=0.4), run_time=0.8)
            delta_syms.append(d_sym)

            self.wait(0.5)

        # ∇L blooms in center
        grad_L = MathTex(r"\nabla L", font_size=100, color=MAGENTA)
        grad_L.set_opacity(0)
        self.add(grad_L)
        self.play(
            grad_L.animate.set_opacity(0.85).scale(1.0),
            run_time=2.5, rate_func=smooth,
        )
        self.wait(1.5)
        self.play(grad_L.animate.set_opacity(0).scale(2.0), run_time=2.0)
        self.remove(grad_L)

        # Hold on fully-lit network
        self.wait(5.0)

        # Second backward sweep, faster
        for li in range(len(layers) - 1, -1, -1):
            col   = delta_colors[li]
            layer = layers[li]
            in_edges = []
            if li > 0:
                in_edges = [
                    e for e in edges
                    if any(
                        np.allclose(e.get_end(), ng[0].get_center(), atol=0.05)
                        for ng in layer
                    )
                ]
            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.7) for ng in layer],
                *([e.animate.set_stroke(col, width=1.8, opacity=0.6) for e in in_edges]),
                run_time=0.6,
            )

        self.wait(3.0)

        # Fade delta syms
        self.play(*[FadeOut(d) for d in delta_syms], run_time=1.5)

        # Fade network to base state
        self.play(
            *[ng[3].animate.set_fill(INDIGO, opacity=0.6) for ng in all_nodes],
            *[ng[0].animate.set_stroke(INDIGO, opacity=0.85, width=2.5) for ng in all_nodes],
            *[e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in edges],
            run_time=2.5,
        )
        self.wait(3.5)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 5 — CHAIN RULE (28s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_chain(self):
        all_nodes = self._all_nodes
        all_edges = self._all_edges

        # Fade network out
        self.play(FadeOut(all_nodes), FadeOut(all_edges), run_time=1.5)

        # 4 colored blocks: h, g, f, L
        block_colors  = [CYAN, INDIGO, VIOLET, RED]
        block_labels  = [r"h", r"g", r"f", r"L"]
        delta_labels  = [r"\delta_1", r"\delta_2", r"\delta_3", ""]
        blocks        = VGroup()
        block_centers = []

        for i, (col, sym) in enumerate(zip(block_colors, block_labels)):
            x = (i - 1.5) * 2.2
            rect = RoundedRectangle(
                width=1.4, height=1.4, corner_radius=0.2,
                fill_color=col, fill_opacity=0.2,
                stroke_color=col, stroke_width=2.5,
            ).move_to(np.array([x, 0.3, 0]))
            label = MathTex(sym, font_size=50, color=col).move_to(rect)
            blocks.add(VGroup(rect, label))
            block_centers.append(np.array([x, 0.3, 0]))

        # Forward arrows
        fwd_arrows = VGroup(*[
            Arrow(
                block_centers[i] + RIGHT * 0.75,
                block_centers[i + 1] + LEFT * 0.75,
                color=WHITE, stroke_width=1.5, buff=0,
                max_tip_length_to_length_ratio=0.25,
            )
            for i in range(3)
        ])

        self.play(
            LaggedStart(*[GrowFromCenter(b) for b in blocks], lag_ratio=0.25),
            run_time=2.0,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in fwd_arrows], lag_ratio=0.3),
            run_time=1.2,
        )
        self.wait(1.0)

        # Backward arrows below + delta labels — RIGHT to LEFT
        back_arrows = VGroup()
        delta_syms  = VGroup()
        for i in range(2, -1, -1):
            ba = Arrow(
                block_centers[i + 1] + LEFT * 0.75 + DOWN * 0.55,
                block_centers[i]     + RIGHT * 0.75 + DOWN * 0.55,
                color=MAGENTA, stroke_width=2.5, buff=0,
                max_tip_length_to_length_ratio=0.3,
            )
            back_arrows.add(ba)
            self.play(GrowArrow(ba), run_time=0.8)

            if delta_labels[i]:
                ds = MathTex(delta_labels[i], font_size=30, color=MAGENTA).next_to(
                    blocks[i], DOWN, buff=1.1
                )
                delta_syms.add(ds)
                self.play(FadeIn(ds, scale=0.5), run_time=0.5)

            # Glow the block
            self.play(
                blocks[i][0].animate.set_stroke(MAGENTA, opacity=0.9).set_fill(MAGENTA, opacity=0.3),
                run_time=0.5,
            )
            self.play(
                blocks[i][0].animate.set_stroke(block_colors[i], opacity=0.9).set_fill(block_colors[i], opacity=0.2),
                run_time=0.6,
            )
            self.wait(0.3)

        self.wait(2.5)

        # Dissolve and bring back full network
        self.play(
            FadeOut(blocks), FadeOut(fwd_arrows), FadeOut(back_arrows), FadeOut(delta_syms),
            run_time=1.5,
        )

        # Rebuild network
        layers, edges, all_nodes, all_edges = make_network_v3(
            [3, 5, 5, 3], center=ORIGIN + UP * 0.15,
            h_gap=2.2, v_gap=0.75, r=0.22, node_color=INDIGO, edge_color=INDIGO,
        )
        self._layers    = layers
        self._edges     = edges
        self._all_nodes = all_nodes
        self._all_edges = all_edges

        self.play(FadeIn(all_edges), FadeIn(all_nodes, lag_ratio=0.05), run_time=2.0)

        # Quick backward sweep with delta colors
        delta_colors = [PINK, MAGENTA, VIOLET, INDIGO]
        for li in range(len(layers) - 1, -1, -1):
            col = delta_colors[li]
            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.8) for ng in layers[li]],
                run_time=0.7,
            )
            self.wait(0.3)
        self.wait(2.0)

        # Reset to base
        self.play(
            *[ng[3].animate.set_fill(INDIGO, opacity=0.6) for ng in all_nodes],
            *[e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in edges],
            run_time=1.5,
        )
        self.wait(1.5)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 6 — EFFICIENCY (17s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_efficiency(self):
        all_nodes = self._all_nodes
        all_edges = self._all_edges
        self.play(FadeOut(all_nodes), FadeOut(all_edges), run_time=1.0)

        # LEFT: dense tangled red web (O(w²))
        bad_nodes_pos = [
            np.array([np.random.uniform(-6.0, -2.5), np.random.uniform(-2.5, 2.5), 0])
            for _ in range(18)
        ]
        bad_nodes = VGroup(*[
            Dot(p, radius=0.06, color=RED, fill_opacity=0.7) for p in bad_nodes_pos
        ])
        bad_edges = VGroup(*[
            Line(bad_nodes_pos[i], bad_nodes_pos[j],
                 stroke_color=RED, stroke_width=0.8, stroke_opacity=0.3)
            for i in range(len(bad_nodes_pos))
            for j in range(i + 1, len(bad_nodes_pos))
            if np.random.rand() < 0.4
        ])
        bad_label = MathTex(r"\mathcal{O}(w^2)", font_size=44, color=RED).move_to(
            LEFT * 4.3 + DOWN * 2.8
        )

        # RIGHT: single elegant gold path (O(w))
        gold_nodes_pos = [
            np.array([-1.0 + i * 0.85, np.sin(i * 0.6) * 0.8, 0])
            for i in range(9)
        ]
        gold_nodes = VGroup(*[
            Dot(p, radius=0.1, color=GOLD, fill_opacity=0.9) for p in gold_nodes_pos
        ])
        gold_path = VGroup(*[
            Line(gold_nodes_pos[i], gold_nodes_pos[i + 1],
                 stroke_color=GOLD, stroke_width=2.5, stroke_opacity=0.9)
            for i in range(len(gold_nodes_pos) - 1)
        ])
        good_label = MathTex(r"\mathcal{O}(w)", font_size=44, color=GOLD).move_to(
            RIGHT * 3.2 + DOWN * 2.8
        )

        # Glow rings around gold nodes
        gold_glow = VGroup(*[
            Circle(radius=0.22, stroke_color=GOLD, stroke_opacity=0.3,
                   stroke_width=1.5, fill_opacity=0).move_to(p)
            for p in gold_nodes_pos
        ])

        # Shift gold to right side
        gold_group = VGroup(gold_nodes, gold_path, gold_glow, good_label)
        gold_group.shift(RIGHT * 2.2)

        self.play(
            LaggedStart(*[GrowFromCenter(n) for n in bad_nodes], lag_ratio=0.04),
            Create(bad_edges, lag_ratio=0.01),
            FadeIn(bad_label),
            run_time=2.5,
        )
        self.play(
            LaggedStart(*[GrowFromCenter(n) for n in gold_nodes], lag_ratio=0.1),
            Create(gold_path),
            FadeIn(good_label),
            run_time=2.0,
        )
        self.play(Create(gold_glow, lag_ratio=0.1), run_time=1.0)

        # Red dims, gold pulses brighter
        self.play(
            bad_nodes.animate.set_fill(RED, opacity=0.2),
            bad_edges.animate.set_stroke(RED, opacity=0.08),
            *[n.animate.set_fill(LGOLD, opacity=1.0) for n in gold_nodes],
            *[e.animate.set_stroke(LGOLD, width=3.5, opacity=1.0) for e in gold_path],
            run_time=3.0,
        )
        self.wait(4.5)

        self.play(
            FadeOut(bad_nodes), FadeOut(bad_edges), FadeOut(bad_label),
            FadeOut(gold_group),
            run_time=2.0,
        )
        self.wait(0.5)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 7 — THE CYCLE (32s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_cycle(self):
        layers, edges, all_nodes, all_edges = make_network_v3(
            [3, 5, 5, 3], center=ORIGIN + UP * 0.15,
            h_gap=2.2, v_gap=0.75, r=0.22, node_color=INDIGO, edge_color=INDIGO,
        )
        self._layers    = layers
        self._edges     = edges
        self._all_nodes = all_nodes
        self._all_edges = all_edges

        self.play(FadeIn(all_edges), FadeIn(all_nodes, lag_ratio=0.04), run_time=1.5)

        # Two full training loops: forward then backward, interleaved
        cycle_fwd_colors = [CYAN,    CYAN]
        cycle_bwd_colors = [MAGENTA, VIOLET]

        for loop_i in range(2):
            fc = cycle_fwd_colors[loop_i]
            bc = cycle_bwd_colors[loop_i]

            # Forward sweep
            for li, layer in enumerate(layers):
                out_edges = [
                    e for e in edges
                    if li < len(layers) - 1 and any(
                        np.allclose(e.get_start(), ng[0].get_center(), atol=0.05)
                        for ng in layer
                    )
                ]
                self.play(
                    *[ng[3].animate.set_fill(fc, opacity=0.7) for ng in layer],
                    *([e.animate.set_stroke(fc, width=1.5, opacity=0.6) for e in out_edges]),
                    run_time=0.55,
                )
                self.play(
                    *[ng[3].animate.set_fill(INDIGO, opacity=0.4) for ng in layer],
                    *([e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in out_edges]),
                    run_time=0.35,
                )

            # ∂L/∂w floats briefly
            dw = MathTex(r"\frac{\partial L}{\partial w}", font_size=30, color=bc)
            dw.move_to(UP * 2.8)
            self.play(FadeIn(dw, scale=0.5), run_time=0.5)

            # Backward sweep
            for li in range(len(layers) - 1, -1, -1):
                layer = layers[li]
                in_edges = [
                    e for e in edges
                    if li > 0 and any(
                        np.allclose(e.get_end(), ng[0].get_center(), atol=0.05)
                        for ng in layer
                    )
                ]
                self.play(
                    *[ng[3].animate.set_fill(bc, opacity=0.8) for ng in layer],
                    *[ng[0].animate.set_stroke(bc, opacity=0.9) for ng in layer],
                    *([e.animate.set_stroke(bc, width=2.0, opacity=0.7) for e in in_edges]),
                    run_time=0.6,
                )
                self.play(
                    *[ng[3].animate.set_fill(INDIGO, opacity=0.5) for ng in layer],
                    *[ng[0].animate.set_stroke(INDIGO, opacity=0.85) for ng in layer],
                    *([e.animate.set_stroke(INDIGO, width=0.6, opacity=0.25) for e in in_edges]),
                    run_time=0.4,
                )

            self.play(FadeOut(dw), run_time=0.5)
            self.wait(0.8)

        # Grand finale: whole network pulses through all colors
        for col in [CYAN, VIOLET, MAGENTA, GOLD]:
            self.play(
                *[ng[3].animate.set_fill(col, opacity=0.85) for ng in all_nodes],
                *[ng[0].animate.set_stroke(col, width=3.5, opacity=1.0) for ng in all_nodes],
                *[e.animate.set_stroke(col, width=1.8, opacity=0.65) for e in edges],
                run_time=0.9,
            )
            self.wait(0.3)

        self.play(
            *[ng[3].animate.set_fill(GOLD, opacity=0.5) for ng in all_nodes],
            *[ng[0].animate.set_stroke(GOLD, width=2.5, opacity=0.7) for ng in all_nodes],
            *[e.animate.set_stroke(GOLD, width=0.8, opacity=0.3) for e in edges],
            run_time=2.0,
        )
        self.wait(4.5)

    # ══════════════════════════════════════════════════════════════════════
    # SCENE 8 — ATARRAIA (14s)
    # ══════════════════════════════════════════════════════════════════════
    def scene_atarraia(self):
        all_nodes = self._all_nodes
        all_edges = self._all_edges
        layers    = self._layers
        edges     = self._edges

        # Network drifts outward slightly (constellation)
        self.play(
            all_nodes.animate.scale(1.25, about_point=ORIGIN),
            all_edges.animate.set_stroke(opacity=0.12, width=0.4),
            run_time=2.5, rate_func=smooth,
        )

        # ATARRAIA brand fades in
        brand = Text("A T A R R A I A", font_size=56, color=GOLD, weight=BOLD)
        self.play(FadeIn(brand, scale=0.7), run_time=2.0)

        # Final MAGENTA wave right-to-left
        for li in range(len(layers) - 1, -1, -1):
            self.play(
                *[ng[0].animate.set_stroke(MAGENTA, opacity=0.6, width=2.0) for ng in layers[li]],
                run_time=0.5,
            )
            self.play(
                *[ng[0].animate.set_stroke(GOLD, opacity=0.4, width=1.5) for ng in layers[li]],
                run_time=0.4,
            )

        self.wait(1.0)

        # Everything fades except brand
        self.play(
            FadeOut(all_nodes), FadeOut(all_edges),
            run_time=2.5,
        )
        self.wait(1.0)
        self.play(FadeOut(brand), run_time=1.5)

    # ── Construct ──────────────────────────────────────────────────────────
    def construct(self):
        self.scene_void()        # 17s
        self.scene_forward()     # 32s
        self.scene_error()       # 17s
        self.scene_backwards()   # 35s
        self.scene_chain()       # 28s
        self.scene_efficiency()  # 17s
        self.scene_cycle()       # 32s
        self.scene_atarraia()    # 14s
        # Total: ~192s
