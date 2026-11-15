import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { cva, type VariantProps } from "class-variance-authority";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import {
  AlertCircle,
  CheckCircle2,
  CircleHelp,
  Download,
  FlaskConical,
  RotateCw,
  X,
} from "lucide-react";
import { download } from "../api";

// shadcn/ui composition: Radix primitives, cva variants, mergeable classes.
const buttonVariants = cva("button", {
  variants: {
    variant: { default: "primary", outline: "outline", ghost: "ghost" },
  },
  defaultVariants: { variant: "default" },
});
export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>
>(({ className, variant, ...props }, ref) => (
  <button
    ref={ref}
    className={twMerge(clsx(buttonVariants({ variant }), className))}
    {...props}
  />
));
Button.displayName = "Button";
export function Modal({
  title,
  children,
  open,
  onClose,
}: {
  title: string;
  children: ReactNode;
  open: boolean;
  onClose: () => void;
}) {
  return (
    <Dialog.Root
      open={open}
      onOpenChange={(value) => {
        if (!value) onClose();
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="modal-overlay" />
        <Dialog.Content className="modal">
          <div className="card-heading">
            <Dialog.Title>{title}</Dialog.Title>
            <Dialog.Close className="icon-button" aria-label="Close details">
              <X />
            </Dialog.Close>
          </div>
          <Dialog.Description className="sr-only">
            Detailed scientific model information for this analysis.
          </Dialog.Description>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={`glass-card ${className}`}>{children}</section>;
}
export function Header({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <header className="page-header">
      <span className="header-icon">
        <FlaskConical size={34} />
      </span>
      <div>
        <div className="eyebrow">JALSATHI / WATER INTELLIGENCE</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <span className="header-badge">
        <span className="live-dot" />
        Academic research workspace
      </span>
    </header>
  );
}
export function Loading() {
  return (
    <div className="skeleton" role="status" aria-label="Loading data">
      <span />
      <span />
      <span />
    </div>
  );
}
export function ErrorState({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  return (
    <div role="alert" className="error-state">
      <AlertCircle />
      <strong>Data unavailable</strong>
      <p>{error instanceof Error ? error.message : "Unable to load data."}</p>
      {retry && (
        <Button variant="outline" onClick={retry}>
          <RotateCw size={16} />
          Retry
        </Button>
      )}
    </div>
  );
}
export function Empty({
  title,
  children,
}: {
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <FlaskConical size={42} />
      </span>
      <h3>{title}</h3>
      {children}
    </div>
  );
}
export function Status({ status }: { status: string }) {
  const Icon =
    status === "within"
      ? CheckCircle2
      : status === "outside"
        ? AlertCircle
        : CircleHelp;
  return (
    <span className={`status ${status}`}>
      <Icon size={16} />
      <span>
        {status === "within"
          ? "Within range"
          : status === "outside"
            ? "Outside range"
            : "Unverified"}
      </span>
    </span>
  );
}
export function ReportButton({ id }: { id: string }) {
  return (
    <Button
      variant="outline"
      onClick={() => void download(`/reports/${id}/pdf`, `JalSathi-${id}.pdf`)}
    >
      <Download size={16} />
      Download Report
    </Button>
  );
}
