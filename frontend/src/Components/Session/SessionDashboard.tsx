// Third Party
import { Card } from 'react-bootstrap';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import { SessionBeltDetails } from '@/Components/Session/Dashboard/SessionBeltDetails';
import { SessionBeltExpectation } from '@/Components/Session/Dashboard/SessionBeltExpectation';
import { SessionBeltStats } from '@/Components/Session/Dashboard/SessionBeltStats';
import { SessionDetails } from '@/Components/Session/Dashboard/SessionDetails';

function SessionDashboard({ sessionData }: { sessionData?: SessionStats }) {
    return (
        <Card.Body>
            <SessionDetails sessionData={sessionData} />
            <SessionBeltDetails sessionData={sessionData} />
            <SessionBeltStats sessionData={sessionData} />
            <SessionBeltExpectation sessionData={sessionData} />
        </Card.Body>
    );
}

export default SessionDashboard;
