#include <cstdlib>

#include <Eigen/Core>
#include <Magnum/EigenIntegration/Integration.h>
#include <Magnum/Math/Vector3.h>

int main() {
    const Eigen::Vector3f eigen{1.0f, 2.0f, 3.0f};
    const Magnum::Vector3 magnum{eigen};

    return magnum == Magnum::Vector3{1.0f, 2.0f, 3.0f} ? EXIT_SUCCESS : EXIT_FAILURE;
}
