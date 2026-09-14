// React
import ReactDOM from "react-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

// AA Belt Radar
import BeltRadarMenu from "./BeltRadarMenu";

const menuRoot = document.getElementById("nav-left");

const BeltRadarMenuAsync = () => {
  const { isLoading, error, data } = useQuery({
    queryKey: ["Menu"],
    queryFn: async () => {
      const api = await axios.get(`/beltradar/api/view/menu`);
      return api.data;
    },
    refetchOnWindowFocus: false,
  });
  if (!menuRoot) {
    return <></>;
  }
  return ReactDOM.createPortal(
    <BeltRadarMenu error={error ? true : false} {...{ isLoading, data }} />,
    menuRoot,
  );
};

export default BeltRadarMenuAsync;
