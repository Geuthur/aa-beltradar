// AA Belt Radar
import type { Session } from "@/Api/schema";
import { SessionBeltDetails } from '@/Components/Session/Partials/BeltDetails';
import { SessionBeltExpectation } from '@/Components/Session/Partials/BeltExpectation';
import { SessionBeltStats } from '@/Components/Session/Partials/BeltStats';
import { SessionDetails } from '@/Components/Session/Partials/SessionDetails';

function SessionDashboard({ sessionData }: { sessionData: Session }) {
    return (
        <>
            <section className="card mt-2" aria-labelledby="session-stats">
                <div className="card-body rounded">
                    <SessionDetails sessionData={sessionData} />
                    <SessionBeltDetails sessionData={sessionData} />
                    <SessionBeltStats sessionData={sessionData} />
                    <SessionBeltExpectation sessionData={sessionData} />
                </div>
            </section>
        </>
    );
}

export default SessionDashboard;
