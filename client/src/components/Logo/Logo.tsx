import "./Logo.scss";

interface LogoProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

/** Kırmızı, kalın MOVIMIND yazı logosu (Poppins). */
export default function Logo({ size = "md", className = "" }: LogoProps) {
  return (
    <span className={`logo logo--${size} ${className}`} aria-label="MOVIMIND">
      <span className="logo__text">
        MOVI<span className="logo__text-accent">MIND</span>
      </span>
    </span>
  );
}
