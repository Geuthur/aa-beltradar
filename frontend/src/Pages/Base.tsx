
// React
import { Outlet } from "react-router";

// Third Party
import { Col } from "react-bootstrap";

// AA Belt Radar
import ErrorBoundary from "@/Components/Loader";
import BeltRadarMenuAsync from "@/Components/Menu/BeltRadarMenuAsync";

const BeltRadarBase = () => {
  return (
    <>
      <BeltRadarMenuAsync />
      <Col>
        <div className="aa-section mt-4">
          <ErrorBoundary>
            <Outlet /> {/* Render the Children here */}
          </ErrorBoundary>
        </div>
      </Col>
    </>
  );
};

export default BeltRadarBase;
