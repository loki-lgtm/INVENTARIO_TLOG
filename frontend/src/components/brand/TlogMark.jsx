import { useId } from "react";

// Símbolo da marca: um T cuja barra superior termina em seta (rota) e tem um
// ponto na base (carga rastreada). Reusado no Sidebar, no Login e no favicon
// (frontend/public/favicon.svg mantém a mesma forma, mas como arquivo estático).
export default function TlogMark({ size = 24, comFundo = true }) {
  const gradId = `tlog-grad-${useId()}`;
  const cor = comFundo ? "#0a0a0b" : "currentColor";

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden="true">
      {comFundo && (
        <>
          <defs>
            <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#e4e4e7" />
              <stop offset="100%" stopColor="#9a9aa3" />
            </linearGradient>
          </defs>
          <rect width="100" height="100" rx="24" fill={`url(#${gradId})`} />
        </>
      )}
      <path d="M20 30 H70" fill="none" stroke={cor} strokeWidth="11" strokeLinecap="round" />
      <path
        d="M66 19 L81 30 L66 41"
        fill="none"
        stroke={cor}
        strokeWidth="9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M45 30 V70" fill="none" stroke={cor} strokeWidth="11" strokeLinecap="round" />
      <circle cx="45" cy="82" r="7" fill={cor} />
    </svg>
  );
}
