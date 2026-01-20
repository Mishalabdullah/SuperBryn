import { Button } from '@/components/ui/button';

function WelcomeImage() {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-center w-16 h-16 rounded-lg border border-border bg-card">
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
    <div ref={ref} className="min-h-screen flex flex-col items-center justify-center px-4 pt-20 relative z-10">
      <section className="bg-background flex flex-col items-center justify-center text-center max-w-3xl">
        <WelcomeImage />

        <h1 className="text-foreground text-4xl md:text-5xl font-bold mb-4 tracking-tight">
          AI Appointment Assistant
        </h1>

        <p className="text-muted-foreground max-w-xl text-lg md:text-xl leading-relaxed mb-12">
          Book, modify, and cancel appointments with natural voice conversation.
        </p>

        <Button
          size="lg"
          onClick={onStartCall}
          className="relative z-20 px-8 py-4 text-base font-semibold rounded-lg bg-red-600 hover:bg-red-700 text-white shadow-lg transition-all"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-8 left-0 flex w-full items-center justify-center px-4 z-10">
        <div className="flex items-center gap-6 text-sm text-muted-foreground">
          <span>Secure</span>
          <span className="w-1 h-1 rounded-full bg-border"></span>
          <span>Fast</span>
          <span className="w-1 h-1 rounded-full bg-border"></span>
          <span>Reliable</span>
        </div>
      </div>
    </div>
  );
};
