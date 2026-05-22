import { useState, useEffect, useRef, useCallback } from 'react'

// ── Stable pseudo-random (avoids Math.random drift on re-renders) ──────
function pr(seed) {
  const x = Math.sin(seed * 9301 + 49297) * 233280
  return x - Math.floor(x)
}

// ── Tile grid data (computed once at module load) ──────────────────────
const COLS = 11
const ROWS = 6
const TILE_W = 84
const TILE_H = 50
const TILE_GAP = 10

const TILES = Array.from({ length: COLS * ROWS }, (_, i) => {
  const col = i % COLS
  const row = Math.floor(i / COLS)
  return {
    id: i,
    col,
    row,
    // Z depth: -45 … +45 px relative to the grid plane
    depth: (pr(i) - 0.5) * 90,
    // Staggered entrance: columns first, then rows, then a small jitter
    delay: col * 0.05 + row * 0.04 + pr(i + 100) * 0.12,
    isSignal: pr(i + 200) < 0.055,            // bright blue "active node"
    isAccent: pr(i + 200) >= 0.055 && pr(i + 200) < 0.24, // tinted tile
    barH: pr(i + 300) < 0.62 ? 0.13 + pr(i + 400) * 0.58 : 0, // speed bar
    barOpacity: 0.32 + pr(i + 500) * 0.52,
  }
})

// ── Injected keyframes + utility classes ──────────────────────────────
// Prefixed with _intro_ to avoid any collision with the page's own CSS.
const INJECTED_CSS = `
  @keyframes _intro_tile_in {
    from { opacity: 0; transform: translateZ(-185px) scale(0.7); }
    to   { opacity: 1; transform: translateZ(var(--itz)) scale(1); }
  }
  @keyframes _intro_text_in {
    from { opacity: 0; transform: translateY(15px); }
  }
  @keyframes _intro_btn_in {
    from { opacity: 0; transform: translateY(12px); }
  }
  @keyframes _intro_btn_pulse {
    0%, 100% { box-shadow: 0 4px 18px rgba(21,101,192,0.28), 0 1px 6px rgba(0,0,0,0.10); }
    50%       { box-shadow: 0 6px 30px rgba(21,101,192,0.54), 0 2px 8px rgba(0,0,0,0.12); }
  }
  @keyframes _intro_signal_glow {
    0%, 100% { box-shadow: 0 0 0 0   rgba(59,130,246,0.00), 0 2px 8px rgba(0,0,0,0.08); }
    50%       { box-shadow: 0 0 0 7px rgba(59,130,246,0.18), 0 2px 8px rgba(0,0,0,0.08); }
  }

  /* CTA button */
  .intro-cta {
    padding: 14px 40px;
    background: #1565c0;
    color: #fff;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    border: none;
    border-radius: 999px;
    cursor: pointer;
    transition: background 0.2s ease, transform 0.15s ease;
    animation: _intro_btn_pulse 2.8s ease-in-out 2s infinite;
    display: block;
  }
  .intro-cta:hover {
    background: #1976d2;
    transform: translateY(-2px) scale(1.025);
  }
  .intro-cta:focus-visible {
    outline: 3px solid rgba(59,130,246,0.65);
    outline-offset: 3px;
  }

`

// ── prefers-reduced-motion hook ────────────────────────────────────────
function useReducedMotion() {
  const [reduced, setReduced] = useState(
    () => typeof window !== 'undefined' &&
          window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const h = (e) => setReduced(e.matches)
    mq.addEventListener('change', h)
    return () => mq.removeEventListener('change', h)
  }, [])
  return reduced
}

// ── Individual tile ────────────────────────────────────────────────────
function TileCell({ tile, reduced }) {
  const { isSignal, isAccent, barH, barOpacity, depth, delay } = tile

  const bg     = isSignal ? '#3b82f6' : isAccent ? '#eff6ff' : '#ffffff'
  const border = isSignal
    ? '1px solid #2563eb'
    : isAccent
      ? '1px solid rgba(59,130,246,0.22)'
      : '1px solid rgba(0,40,120,0.07)'

  const tileAnim = reduced
    ? 'none'
    : [
        `_intro_tile_in 0.55s cubic-bezier(0.16,1,0.3,1) ${delay}s both`,
        isSignal ? `_intro_signal_glow 2.8s ease-in-out ${delay + 0.65}s infinite` : '',
      ].filter(Boolean).join(', ')

  return (
    <div
      style={{
        width: TILE_W,
        height: TILE_H,
        borderRadius: 8,
        background: bg,
        border,
        boxShadow: isSignal
          ? '0 0 20px rgba(59,130,246,0.3), 0 2px 8px rgba(0,0,0,0.08)'
          : '0 2px 10px rgba(0,0,0,0.055), 0 1px 3px rgba(0,0,0,0.03)',
        position: 'relative',
        overflow: 'hidden',
        flexShrink: 0,
        // CSS var used in the @keyframes to clause
        '--itz': `${depth}px`,
        // Static position (used when reduced motion is on)
        transform: `translateZ(${depth}px) scale(1)`,
        animation: tileAnim,
      }}
    >
      {/* Speed bar — represents a broadband measurement */}
      {barH > 0 && (
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: `${barH * 100}%`,
          height: isSignal ? 4 : 3,
          background: isSignal
            ? 'rgba(255,255,255,0.55)'
            : `rgba(59,130,246,${barOpacity})`,
          borderRadius: '0 2px 0 0',
        }} />
      )}

      {/* Signal dot on active-node tiles */}
      {isSignal && (
        <div style={{
          position: 'absolute',
          top: 9,
          right: 9,
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.85)',
        }} />
      )}
    </div>
  )
}

// ── Main overlay ───────────────────────────────────────────────────────
export default function IntroOverlay() {
  const [visible,  setVisible]  = useState(() => !sessionStorage.getItem('intro-seen'))
  const [exiting,  setExiting]  = useState(false)
  const reducedMotion = useReducedMotion()

  const sceneRef    = useRef(null)
  const btnRef      = useRef(null)
  const targetRot   = useRef({ x: 0, y: 0 })
  const currentRot  = useRef({ x: 0, y: 0 })
  const rafRef      = useRef(null)
  const autoAngle   = useRef(0)

  // Inject keyframes + utility CSS into <head> (cleaned up on unmount)
  useEffect(() => {
    const el = document.createElement('style')
    el.textContent = INJECTED_CSS
    document.head.appendChild(el)
    return () => el.remove()
  }, [])

  // Move keyboard focus to the CTA after the tile animation settles
  useEffect(() => {
    if (!visible) return
    const t = setTimeout(
      () => btnRef.current?.focus({ preventScroll: true }),
      reducedMotion ? 800 : 2300
    )
    return () => clearTimeout(t)
  }, [visible, reducedMotion])

  const dismiss = useCallback(() => {
    if (exiting) return
    setExiting(true)
    sessionStorage.setItem('intro-seen', '1')
    setTimeout(() => {
      setVisible(false)
      // Scroll so the first chart is in view immediately after the overlay leaves
      const target = document.getElementById('chart1')
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 660)
  }, [exiting])

  // Escape key shortcut
  useEffect(() => {
    if (!visible) return
    const h = (e) => { if (e.key === 'Escape') dismiss() }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [visible, dismiss])

  // Mouse-parallax + subtle auto-drift (skipped for reduced motion)
  useEffect(() => {
    if (!visible || reducedMotion) return

    const onMouseMove = (e) => {
      targetRot.current = {
        x: (e.clientY / window.innerHeight - 0.5) * -10,
        y: (e.clientX / window.innerWidth  - 0.5) *  16,
      }
    }

    const tick = () => {
      autoAngle.current += 0.004
      // Gentle drift on Y when mouse is idle
      targetRot.current.y += Math.sin(autoAngle.current) * 0.022

      // Lerp toward target for smooth movement
      currentRot.current.x += (targetRot.current.x - currentRot.current.x) * 0.04
      currentRot.current.y += (targetRot.current.y - currentRot.current.y) * 0.04

      if (sceneRef.current) {
        const rx = 24 + currentRot.current.x
        const ry = currentRot.current.y
        sceneRef.current.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg)`
      }
      rafRef.current = requestAnimationFrame(tick)
    }

    window.addEventListener('mousemove', onMouseMove, { passive: true })
    rafRef.current = requestAnimationFrame(tick)

    return () => {
      window.removeEventListener('mousemove', onMouseMove)
      cancelAnimationFrame(rafRef.current)
    }
  }, [visible, reducedMotion])

  if (!visible) return null

  // Max tile delay: (COLS-1)*0.05 + (ROWS-1)*0.04 + 0.12 ≈ 0.82 s
  // Tile animation: 0.55 s → all tiles done by ~1.37 s
  // Text starts at 1.48 s to let the grid fully settle first.
  const T = {
    label : '1.48s',
    title : '1.63s',
    divider: '1.72s',
    sub   : '1.80s',
    btn   : '2.00s',
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Intro: Australia's Broadband Divide"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'linear-gradient(155deg, #f8fafc 0%, #eef4fb 55%, #e8f0f9 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        // Exit transition
        opacity: exiting ? 0 : 1,
        transform: exiting ? 'scale(1.03)' : 'scale(1)',
        transition: exiting ? 'opacity 0.66s ease, transform 0.66s ease' : 'none',
      }}
    >
      {/* ─────────── 3-D tile grid ─────────────────────────────────── */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          perspective: '900px',
          perspectiveOrigin: '50% 50%',
          pointerEvents: 'none',
          overflow: 'hidden',
        }}
      >
        <div
          ref={sceneRef}
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${COLS}, ${TILE_W}px)`,
            gridTemplateRows: `repeat(${ROWS}, ${TILE_H}px)`,
            gap: TILE_GAP,
            transformStyle: 'preserve-3d',
            // Base tilt: looking slightly down at the data grid
            transform: reducedMotion
              ? 'rotateX(24deg)'
              : 'rotateX(24deg) rotateY(0deg)',
          }}
        >
          {TILES.map((tile) => (
            <TileCell key={tile.id} tile={tile} reduced={reducedMotion} />
          ))}
        </div>
      </div>

      {/* ─────────── Radial vignette — clears center for text ─────── */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 70% 60% at 50% 50%, ' +
            'rgba(248,250,252,0.93) 0%, rgba(238,244,251,0.68) 50%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />

      {/* ─────────── Edge fades ────────────────────────────────────── */}
      <div aria-hidden="true" style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: '32%',
        background: 'linear-gradient(to top, rgba(232,240,249,0.96) 0%, transparent 100%)',
        pointerEvents: 'none',
      }} />
      <div aria-hidden="true" style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: '22%',
        background: 'linear-gradient(to bottom, rgba(248,250,252,0.90) 0%, transparent 100%)',
        pointerEvents: 'none',
      }} />

      {/* ─────────── Text content ──────────────────────────────────── */}
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          textAlign: 'center',
          padding: '0 24px',
          maxWidth: 620,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Eyebrow label */}
        <span style={{
          fontSize: '0.7rem',
          fontWeight: 700,
          letterSpacing: '0.16em',
          textTransform: 'uppercase',
          color: '#3b82f6',
          marginBottom: 18,
          animation: reducedMotion ? 'none' : `_intro_text_in 0.55s ease ${T.label} both`,
        }}>
          FIT2179 Data Visualisation 2
        </span>

        {/* Main title */}
        <h1 style={{
          fontSize: 'clamp(2.1rem, 5.5vw, 3.7rem)',
          fontWeight: 800,
          color: '#0f172a',
          letterSpacing: '-0.03em',
          lineHeight: 1.1,
          margin: '0 0 20px',
          animation: reducedMotion ? 'none' : `_intro_text_in 0.6s ease ${T.title} both`,
        }}>
          Australia&apos;s<br />
          <span style={{ color: '#1565c0' }}>Broadband Divide</span>
        </h1>

        {/* Accent bar */}
        <div aria-hidden="true" style={{
          width: 48,
          height: 3,
          borderRadius: 2,
          background: 'linear-gradient(90deg, #3b82f6, #1565c0)',
          marginBottom: 20,
          animation: reducedMotion ? 'none' : `_intro_text_in 0.5s ease ${T.divider} both`,
        }} />

        {/* Subtitle */}
        <p style={{
          fontSize: 'clamp(0.92rem, 2vw, 1.1rem)',
          color: '#475569',
          lineHeight: 1.72,
          margin: '0 0 40px',
          maxWidth: 430,
          animation: reducedMotion ? 'none' : `_intro_text_in 0.55s ease ${T.sub} both`,
        }}>
          How NBN speed and technology differ across Australian communities.
        </p>

        {/* CTA wrapper handles the entrance; the button handles hover + pulse */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          animation: reducedMotion ? 'none' : `_intro_btn_in 0.5s cubic-bezier(0.16,1,0.3,1) ${T.btn} both`,
        }}>
          <button
            ref={btnRef}
            className="intro-cta"
            onClick={dismiss}
            aria-label="Explore the data — close intro and view the visualisation"
          >
            Explore the data →
          </button>

        </div>
      </div>
    </div>
  )
}
