// AA Belt Radar
import type { Session } from "@/Api/schema";
import { SessionBeltDetails } from '@/Components/Session/Dashboard/SessionBeltDetails';
import { SessionBeltExpectation } from '@/Components/Session/Dashboard/SessionBeltExpectation';
import { SessionBeltStats } from '@/Components/Session/Dashboard/SessionBeltStats';
import { SessionDetails } from '@/Components/Session/Dashboard/SessionDetails';

function SessionDashboard({ sessionData }: { sessionData?: Session }) {
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
