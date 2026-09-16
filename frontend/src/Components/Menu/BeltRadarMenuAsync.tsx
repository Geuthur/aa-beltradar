// React
import ReactDOM from "react-dom";

// Third Party
import { useQuery } from "@tanstack/react-query";

// AA Belt Radar
import { loadMenu } from "@/Api/BeltRadar"
import BeltRadarMenu from "@/Components/Menu/BeltRadarMenu";
import { queryKeys } from "@/Api/query";

const menuRoot = document.getElementById("nav-left");

const BeltRadarMenuAsync = () => {
  const { isLoading, error, data } = useQuery({
    queryKey: queryKeys.Menu,
    queryFn: () => loadMenu(),
    refetchOnWindowFocus: false,
  });

  if (!menuRoot || !data?.links) {
    return <></>;
  }

  return ReactDOM.createPortal(
    <BeltRadarMenu error={error ? true : false} isLoading={isLoading} data={data.links} />,
    menuRoot,
  );
};

export default BeltRadarMenuAsync;
