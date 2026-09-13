// Decorative Korean-cityscape illustration for the login page - hanok roof,
// lantern, cherry blossoms, mountains, river/bridge, skyline, sun. Purely
// decorative background art, flat/layered SVG shapes (no photo assets).
export default function KoreanCityscape({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 900 620"
      fill="none"
      className={className}
      aria-hidden="true"
      preserveAspectRatio="xMinYMax slice"
    >
      {/* sun */}
      <circle cx="620" cy="430" r="72" fill="#FFD43B" opacity="0.9" />

      {/* far mountains */}
      <path
        d="M180 480 L300 380 L400 450 L480 360 L600 460 L900 400 L900 620 L180 620 Z"
        fill="#C9BEEA"
        opacity="0.55"
      />
      {/* near mountains */}
      <path
        d="M0 520 L140 420 L260 500 L360 430 L520 510 L700 440 L900 500 L900 620 L0 620 Z"
        fill="#B3A5E0"
        opacity="0.6"
      />

      {/* skyline silhouette */}
      <g fill="#A497D6" opacity="0.75">
        <rect x="330" y="470" width="26" height="70" />
        <rect x="362" y="450" width="22" height="90" />
        <rect x="392" y="480" width="30" height="60" />
        <rect x="430" y="460" width="20" height="80" />
        <rect x="458" y="490" width="26" height="50" />
      </g>
      {/* tower */}
      <g stroke="#8C7BC7" strokeWidth="4" opacity="0.85">
        <line x1="345" y1="330" x2="345" y2="470" />
        <line x1="325" y1="470" x2="365" y2="470" />
        <line x1="333" y1="440" x2="357" y2="440" />
      </g>
      <circle cx="345" cy="330" r="6" fill="#E14D4D" opacity="0.85" />
      <circle cx="345" cy="355" r="5" fill="#E14D4D" opacity="0.7" />

      {/* river */}
      <rect x="0" y="540" width="900" height="80" fill="#CFC3ED" opacity="0.45" />
      <path d="M0 555 Q 200 545 400 558 T 900 552" stroke="#FFFFFF" strokeWidth="3" opacity="0.4" fill="none" />

      {/* bridge */}
      <g stroke="#8C7BC7" strokeWidth="4" opacity="0.8" fill="none">
        <path d="M260 560 Q 430 520 600 560" />
        <line x1="300" y1="560" x2="300" y2="600" />
        <line x1="360" y1="547" x2="360" y2="600" />
        <line x1="430" y1="540" x2="430" y2="600" />
        <line x1="500" y1="547" x2="500" y2="600" />
        <line x1="560" y1="560" x2="560" y2="600" />
      </g>

      {/* hanok roof (top-left) */}
      <g>
        <path
          d="M-20 210 Q 60 120 140 150 Q 190 100 260 140 Q 320 110 380 160 L 380 200 L -20 200 Z"
          fill="#3B3552"
        />
        <path
          d="M-20 200 L 380 200 L 380 220 Q 200 250 -20 222 Z"
          fill="#544C77"
        />
        <rect x="30" y="220" width="14" height="130" fill="#6B5D4A" opacity="0.9" />
        <rect x="0" y="345" width="140" height="10" fill="#6B5D4A" opacity="0.9" />
      </g>

      {/* lantern hanging under the eave */}
      <g>
        <line x1="90" y1="230" x2="90" y2="270" stroke="#6B5D4A" strokeWidth="3" />
        <ellipse cx="90" cy="300" rx="26" ry="34" fill="#FFD43B" opacity="0.9" />
        <ellipse cx="90" cy="300" rx="26" ry="34" fill="#FFD43B" opacity="0.35">
          <animate attributeName="opacity" values="0.35;0.6;0.35" dur="3.5s" repeatCount="indefinite" />
        </ellipse>
        <rect x="82" y="332" width="16" height="6" fill="#8C6E4A" />
        <line x1="90" y1="338" x2="90" y2="360" stroke="#E14D4D" strokeWidth="2" />
      </g>

      {/* cherry blossom branch, top-left corner */}
      <g stroke="#6B5D4A" strokeWidth="3" fill="none" opacity="0.9">
        <path d="M-10 20 Q 60 40 110 10 Q 150 -10 190 30" />
        <path d="M40 25 Q 50 55 30 80" />
        <path d="M120 15 Q 140 45 130 75" />
      </g>
      <g fill="#F7B8C9">
        {[
          [10, 15], [30, 30], [55, 10], [80, 35], [105, 15], [130, 40], [155, 20], [175, 45],
          [45, 60], [120, 55], [25, 75],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r={9 - (i % 3)} opacity={0.85} />
        ))}
      </g>
      {/* falling petals scattered further out */}
      <g fill="#F7B8C9" opacity="0.7">
        <ellipse cx="230" cy="90" rx="6" ry="4" transform="rotate(20 230 90)" />
        <ellipse cx="300" cy="150" rx="5" ry="3.5" transform="rotate(-15 300 150)" />
        <ellipse cx="210" cy="200" rx="6" ry="4" transform="rotate(40 210 200)" />
        <ellipse cx="650" cy="120" rx="5" ry="3.5" transform="rotate(10 650 120)" />
        <ellipse cx="750" cy="220" rx="6" ry="4" transform="rotate(-25 750 220)" />
      </g>
    </svg>
  )
}
