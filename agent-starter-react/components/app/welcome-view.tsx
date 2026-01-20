import { Button } from '@/components/ui/button';

function WelcomeImage() {
  return (
    <div className="mb-8">
      <div className="border-border bg-card flex h-16 w-16 items-center justify-center rounded-lg border">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-foreground"
        >
          <path
            d="M8 2v3m8-3v3M3.5 9.09h17M21 8.5V17c0 3-1.5 5-5 5H8c-3.5 0-5-2-5-5V8.5c0-3 1.5-5 5-5h8c3.5 0 5 2 5 5Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeMiterlimit="10"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M15.694 13.7h.009M15.694 16.7h.009M11.995 13.7h.01M11.995 16.7h.01M8.294 13.7h.01M8.294 16.7h.01"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div
      ref={ref}
      className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 pt-20"
    >
      <section className="bg-background flex max-w-3xl flex-col items-center justify-center text-center">
        <WelcomeImage />

        <h1 className="text-foreground mb-4 text-4xl font-bold tracking-tight md:text-5xl">
          AI Appointment Assistant
        </h1>

        <p className="text-muted-foreground mb-12 max-w-xl text-lg leading-relaxed md:text-xl">
          Book, modify, and cancel appointments with natural voice conversation.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="relative z-20 rounded-lg bg-red-600 px-8 py-4 text-base font-semibold text-white shadow-lg transition-all hover:bg-red-700"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-8 left-0 z-10 flex w-full items-center justify-center px-4">
        <div className="text-muted-foreground flex items-center gap-6 text-sm">
          <span>Secure</span>
          <span className="bg-border h-1 w-1 rounded-full"></span>
          <span>Fast</span>
          <span className="bg-border h-1 w-1 rounded-full"></span>
          <span>Reliable</span>
        </div>
      </div>
    </div>
  );
};
