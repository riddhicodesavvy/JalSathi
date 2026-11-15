export function Logo() {
  return (
    <div className="brand">
      <svg width="48" height="64" viewBox="0 0 48 64" aria-hidden="true">
        <defs>
          <linearGradient id="drop" x2="1" y2="1">
            <stop stopColor="#c7f5ff" />
            <stop offset="1" stopColor="#09a5e6" />
          </linearGradient>
        </defs>
        <path
          d="M24 2C19 14 3 31 3 42a21 21 0 0 0 42 0C45 31 29 14 24 2Z"
          fill="url(#drop)"
          stroke="#c4f2ff"
        />
        <path
          d="M24 56C7 55 8 38 8 38c13 0 17 8 16 18Zm1 0c-2-17 12-23 15-23 3 16-8 22-15 23Z"
          fill="#5bd171"
          stroke="#e6fff4"
          strokeWidth="2"
        />
      </svg>
      <div>
        <strong>JalSathi</strong>
        <span>Water Quality Intelligence</span>
      </div>
    </div>
  );
}
export function Waves() {
  return (
    <svg
      className="water-waves"
      viewBox="0 0 1400 160"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="wave">
          <stop stopColor="#e3f7ff" stopOpacity="0" />
          <stop offset=".5" stopColor="#34c8e4" stopOpacity=".4" />
          <stop offset="1" stopColor="#0c9dc9" stopOpacity=".2" />
        </linearGradient>
      </defs>
      <path
        d="M0 100C250 190 330-60 650 55S1000 150 1400 20V160H0Z"
        fill="url(#wave)"
      />
      <path
        d="M0 130C300 40 400 200 700 85S1120 130 1400 50"
        fill="none"
        stroke="#36bfde"
        strokeOpacity=".3"
        strokeWidth="3"
      />
      <path
        d="M0 120C400 210 470-20 740 70S1100 180 1400 70V160H0Z"
        fill="url(#wave)"
      />
    </svg>
  );
}
export function LabArt() {
  return (
    <div className="lab-art" aria-hidden="true">
      <svg viewBox="0 0 240 250">
        <defs>
          <linearGradient id="flask" x2="1" y2="1">
            <stop stopColor="#d2fbff" stopOpacity=".7" />
            <stop offset=".5" stopColor="#15b4de" stopOpacity=".3" />
            <stop offset="1" stopColor="#d9ffff" />
          </linearGradient>
          <linearGradient id="liquid" x2="0" y2="1">
            <stop stopColor="#0de4e5" />
            <stop offset="1" stopColor="#0172ad" />
          </linearGradient>
        </defs>
        <path
          d="M75 28h48v10h-8v62l40 103q9 25-18 25H60q-26 0-16-25l40-103V38h-9Z"
          fill="url(#flask)"
          stroke="#c1f9ff"
          strokeWidth="3"
        />
        <path
          d="M67 158q35 15 65 0l20 48q5 16-15 16H61q-20 0-13-17Z"
          fill="url(#liquid)"
        />
        <path
          d="M91 43v62l-34 92"
          fill="none"
          stroke="white"
          strokeWidth="4"
          opacity=".6"
        />
        <path
          d="M167 59h25v120q-12 28-25 0Z"
          fill="url(#flask)"
          stroke="#b0f5ff"
          strokeWidth="3"
        />
        <path d="M170 130h19v48q-9 19-19 0Z" fill="#0cc8df" />
        <path
          d="M16 220q0-50 30-65-2 42-30 65Zm0-10q-25-35-9-64 24 21 9 64Z"
          fill="#58c964"
        />
        <g fill="white" opacity=".7">
          <circle cx="91" cy="182" r="4" />
          <circle cx="110" cy="202" r="6" />
          <circle cx="82" cy="210" r="3" />
        </g>
      </svg>
      <span>
        Smarter water insights.
        <br />
        Powered by machine learning.
      </span>
    </div>
  );
}
