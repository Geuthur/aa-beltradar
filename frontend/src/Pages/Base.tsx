
// React
import { Outlet } from "react-router";

// Third Party
import { Col } from "react-bootstrap";

// AA Belt Radar
import BeltRadarMenuAsync from "@/Components/Menu/BeltRadarMenuAsync";

const BeltRadarBase = () => {
  return (
    <>
      <BeltRadarMenuAsync />
      <Col>
        <div className="mt-4">
          <Outlet /> {/* Render the Children here */}
        </div>
      </Col>
    </>
  );
};

export default BeltRadarBase;
