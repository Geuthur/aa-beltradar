// Third Party
import { Globe, Lock } from "lucide-react";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { renderTooltip } from "@/Components/Tables/BaseTable/tableHelper";

export function PublicBadge({ isPublic }: { isPublic: boolean }) {
  const { t } = useTranslation();
  const label = isPublic ? t("Public") : t("Private");

  return renderTooltip(
    label,
    <span
      className={`br-btn br-btn-sm ${isPublic ? "br-btn-success" : "br-btn-secondary"}`}
      role="img"
      aria-label={label}
    >
      {isPublic ? <Globe size={14} aria-hidden="true" /> : <Lock size={14} aria-hidden="true" />}
    </span>,
  );
}

export default PublicBadge;
